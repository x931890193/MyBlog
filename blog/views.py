# coding=utf-8
import json
import random
import traceback
from collections import Counter
from datetime import datetime, timedelta

import pymongo
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import F, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.http import urlquote
from django.views.decorators.csrf import csrf_exempt, csrf_protect, ensure_csrf_cookie
from django.views.decorators.http import require_POST

from MyBlog.settings import MEDIA_URL, logger
from MyBlog.utils import redis_client
from .forms import Searchform, Tagform
from .models import Article, Acimage, Category, SponsorLead, SponsorAd
from .seo import TOOL_PAGES, STATIC_SITEMAP_PAGES, absolute_url, meta_description, tool_by_slug
from spider.utils import mongodb


def clean_text(value, max_length):
    value = (value or '').strip()
    if max_length and len(value) > max_length:
        return value[:max_length]
    return value


def client_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if forwarded:
        return forwarded.split(',')[0].strip()[:45] or None
    return request.META.get('HTTP_X_REAL_IP') or request.META.get('REMOTE_ADDR') or None


def positive_int(value, default=1):
    try:
        value = int(value)
    except (TypeError, ValueError):
        return default
    return value if value > 0 else default


def article_queryset():
    return Article.objects.filter(article_type='2').select_related('article_user', 'article_category')


def media_absolute_url(path):
    path = str(path or '').strip()
    if not path:
        return ''
    return absolute_url('%s%s' % (MEDIA_URL, path))


def tag_url_path(tag):
    return '/tag/%s/' % urlquote((tag or '').strip(), safe='')


def popular_article_tags(limit=80):
    counter = Counter()
    values = Article.objects.filter(article_type='2').exclude(article_tag='') \
        .values_list('article_tag', flat=True).order_by('-article_create_time')[:2000]
    for value in values:
        counter.update([tag for tag in (value or '').split() if tag])
    return [tag for tag, count in counter.most_common(limit)]


def related_articles_for(article, tags, limit=6):
    query = Q()
    if getattr(article, 'article_category_id', None):
        query |= Q(article_category_id=article.article_category_id)
    for tag in tags:
        query |= Q(article_tag__contains=tag)

    base = article_queryset().exclude(pk=article.pk)
    if query.children:
        related = list(base.filter(query).distinct().order_by('-article_click', '-article_create_time')[:limit])
        if related:
            return related
    return list(base.order_by('-article_click', '-article_create_time')[:limit])


TECH_CATEGORY_IDS = (1, 2, 3)
TECH_CATEGORY_ALIASES = (
    'python', 'python编程',
    'go', 'go语言', 'golang',
    'liunx', 'linux', 'operation', '运维',
)


def grouped_category_ids(group):
    if group != 'tech':
        return []
    categories = Category.objects.filter(pk__in=TECH_CATEGORY_IDS)
    ids = list(categories.values_list('id', flat=True))
    if ids:
        return ids
    query = Q()
    for alias in TECH_CATEGORY_ALIASES:
        query |= Q(category_name__icontains=alias)
    return list(Category.objects.filter(query).values_list('id', flat=True))


def collection_count(collection):
    try:
        return collection.estimated_document_count()
    except Exception:
        return collection.find().count()


def random_document(collection, fallback_id=1):
    total = collection_count(collection)
    if total <= 0:
        return None
    random_id = random.randint(1, total)
    return collection.find_one({'id': random_id}) or collection.find_one({'id': fallback_id}) or collection.find_one()


def music_payload(document):
    if not document:
        return {}
    lrc = document.get('format_lrc') or []
    if not isinstance(lrc, list):
        lrc = []
    return {
        'title': document.get('title') or 'Random Music',
        'author': document.get('author') or 'Mongona Radio',
        'images': document.get('images') or '',
        'mp3_url': document.get('mp3_url') or '',
        'comment_nickname': document.get('comment_nickname') or '',
        'comment_content': document.get('comment_content') or '',
        'comment_pub_date': document.get('comment_pub_date') or '',
        'format_lrc': lrc,
    }


def random_music_api(request):
    data = music_payload(random_document(mongodb['music']) or {})
    if not data or not data.get('mp3_url'):
        return JsonResponse({'code': 1, 'msg': 'music not found', 'data': {}})
    return JsonResponse({'code': 0, 'msg': None, 'data': data})


def sponsor_ad_redirect(request, ad_id):
    now = timezone.now()
    ad = SponsorAd.objects.filter(pk=ad_id, is_active=True).filter(
        Q(start_at__isnull=True) | Q(start_at__lte=now),
        Q(end_at__isnull=True) | Q(end_at__gte=now),
    ).first()
    if not ad:
        return redirect('/sponsor/#lead-form')
    SponsorAd.objects.filter(pk=ad.pk).update(click_count=F('click_count') + 1)
    return redirect(ad.target_url)


@require_POST
@csrf_exempt
def sponsor_ad_event_api(request):
    data = request.POST
    if not data and request.body:
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            data = {}
    try:
        ad_id = int(data.get('ad_id'))
    except (TypeError, ValueError):
        return JsonResponse({'code': 1, 'msg': 'invalid ad id'}, status=400)
    event = clean_text(data.get('event'), 32)
    field_map = {
        'impression': 'impression_count',
        'dismiss': 'dismiss_count',
    }
    field = field_map.get(event)
    if not field:
        return JsonResponse({'code': 1, 'msg': 'invalid event'}, status=400)

    now = timezone.now()
    updated = SponsorAd.objects.filter(pk=ad_id, is_active=True).filter(
        Q(start_at__isnull=True) | Q(start_at__lte=now),
        Q(end_at__isnull=True) | Q(end_at__gte=now),
    ).update(**{field: F(field) + 1})
    return JsonResponse({'code': 0, 'msg': None, 'updated': bool(updated)})


@require_POST
@csrf_protect
def sponsor_lead_api(request):
    ip = client_ip(request)
    throttle_key = 'sponsor_lead_submit:%s' % (ip or 'unknown')
    try:
        if redis_client.get(throttle_key):
            return JsonResponse({'code': 1, 'msg': '提交太频繁，请稍后再试。'}, status=429)
    except Exception as e:
        logger.warning(e)

    if clean_text(request.POST.get('website'), 120):
        return JsonResponse({'code': 0, 'msg': '需求已收到，我会尽快联系你。'})

    name = clean_text(request.POST.get('name'), 80)
    company = clean_text(request.POST.get('company'), 120)
    contact = clean_text(request.POST.get('contact'), 160)
    demand_type = clean_text(request.POST.get('demand_type'), 32) or 'sponsor'
    budget = clean_text(request.POST.get('budget'), 32) or 'unknown'
    message = clean_text(request.POST.get('message'), 2000)
    source_path = clean_text(request.POST.get('source_path'), 512) or clean_text(request.META.get('HTTP_REFERER'), 512)

    valid_demands = [item[0] for item in SponsorLead.DEMAND_CHOICES]
    valid_budgets = [item[0] for item in SponsorLead.BUDGET_CHOICES]
    if demand_type not in valid_demands:
        demand_type = 'other'
    if budget not in valid_budgets:
        budget = 'unknown'
    if not name:
        return JsonResponse({'code': 1, 'msg': '请填写称呼。'}, status=400)
    if not contact:
        return JsonResponse({'code': 1, 'msg': '请填写联系方式。'}, status=400)

    lead = SponsorLead.objects.create(
        name=name,
        company=company,
        contact=contact,
        demand_type=demand_type,
        budget=budget,
        message=message,
        source_path=source_path,
        referer=clean_text(request.META.get('HTTP_REFERER'), 1024),
        user_agent=clean_text(request.META.get('HTTP_USER_AGENT'), 512),
        ip=ip,
    )
    try:
        redis_client.setex(throttle_key, 60, 1)
    except Exception as e:
        logger.warning(e)
    return JsonResponse({'code': 0, 'msg': '需求已收到，我会尽快联系你。', 'data': {'id': lead.id}})


def bloglist(request):
    page_url = request.get_full_path()
    c = request.GET.get('c', '')  # 分类
    g = request.GET.get('g', '').strip().lower()  # 聚合分类
    if c:
        try:
            c = int(c)
        except ValueError:
            return render(request, '404.html', status=404)
        if c == 4:
            images = Acimage.objects.all().order_by('-time_create')
            music_data = music_payload(random_document(mongodb['music']) or {})
            return render(request, 'gallery/image.html',
                          {'images': images, 'music_data': music_data, 'page_url': page_url,
                           'category_name': "Gallery"})
        elif c == 5:
            comment_data = random_document(mongodb['music']) or {}
            return render(request, 'life/life.html', {'data': comment_data, 'page_url': page_url})
        elif c == 6:
            try:
                video = random_document(mongodb['video'])
            except Exception as e:
                logger.error(e)
                video = [
                    {
                        'title': '大郎吃药！',
                        'src': 'https://cdn.mongona.com/static/vedio/574bc7a8a155230177a912beb3d1f4.MP4',
                        'describe': "It's time for Dalang to take his medicine "
                    }
                ]
            return render(request, 'about/about.html', {'video': video, 'page_url': page_url})

    # 获取当前页码，用来控制翻页中当前页码的class="{% if p == page_number %}am-active {% endif %}"
    page_number = positive_int(request.GET.get('p'), 1)
    s = ''  # 搜索关键字
    t = ''  # TAG关键字
    d = request.GET.get('d', '')  # 默认文章归档
    if request.method == 'GET':
        form_s = Searchform(request.GET)
        form_t = Tagform(request.GET)

        if form_s.is_valid():
            s = request.GET.get('s')
        if form_t.is_valid():
            t = request.GET.get('t')
    category_name = '富强，民主，文明，和谐，自由，平等，公正，法治，爱国，敬业，诚信，友善。'
    articles = article_queryset()
    if c:
        # 分类页
        articles = articles.filter(article_category=c).order_by('-article_create_time')
        try:
            category_name = Category.objects.get(pk=c).category_detail
        except Exception as e:
            traceback.print_exc()
            logger.error(e)
    elif g == 'tech':
        category_ids = grouped_category_ids(g)
        if category_ids:
            articles = articles.filter(article_category_id__in=category_ids).order_by('-article_create_time')
        else:
            articles = articles.none()
        category_name = 'Tech：Python / Go / Operation'
    elif s:
        # 搜索结果
        articles = articles.filter(Q(article_title__contains=s) | Q(article_content__contains=s)) \
            .order_by('-article_create_time')
    elif t:
        # 标签页搜索结果
        articles = articles.filter(article_tag__contains=t).order_by('-article_create_time')

    elif d:
        # 文章归档 创建时间对象，然后取年，月，利用filter来取相关时间的日志。
        try:
            md = datetime.strptime(d, "%Y-%m")
        except ValueError:
            return render(request, '404.html', status=404)
        articles = articles.filter(article_create_time__year=md.year, article_create_time__month=md.month) \
            .order_by('-article_create_time')
    else:
        # 否则全部文章
        articles = articles.order_by('-article_create_time')

    paginator = Paginator(articles, 8)  # 第二个参数是每页显示的数量
    try:
        contacts = paginator.page(page_number)
    except PageNotAnInteger:
        contacts = paginator.page(1)
    except EmptyPage:
        contacts = paginator.page(paginator.num_pages)
    pages = pagesHelp(page_number, paginator.num_pages, 6)

    return render(request, 'blog/list.html', {'articles': articles,
                                              'contacts': contacts,
                                              'category_name': category_name,
                                              'c': c,
                                              'g': g,
                                              's': s,
                                              'd': d,
                                              't': t,
                                              'page_url': page_url,
                                              'canonical_url': absolute_url(page_url),
                                              'seo_title': category_name,
                                              'seo_description': meta_description(
                                                  category_name,
                                                  'Mongona 技术博客，记录 Python、Django、Go、Linux、AI、运维和开发工具实践。',
                                              ),
                                              'page_number': page_number,
                                              'pages': pages})


def tag_landing(request, tag):
    tag = clean_text(tag, 120)
    if not tag:
        return render(request, '404.html', status=404)

    page_number = positive_int(request.GET.get('p'), 1)
    articles = article_queryset().filter(article_tag__contains=tag).order_by('-article_create_time')
    paginator = Paginator(articles, 8)
    try:
        contacts = paginator.page(page_number)
    except PageNotAnInteger:
        contacts = paginator.page(1)
    except EmptyPage:
        contacts = paginator.page(paginator.num_pages)
    pages = pagesHelp(page_number, paginator.num_pages, 6)
    page_path = tag_url_path(tag)
    category_name = '%s 技术专题' % tag

    return render(request, 'blog/list.html', {
        'articles': articles,
        'contacts': contacts,
        'category_name': category_name,
        'c': '',
        'g': '',
        's': '',
        'd': '',
        't': tag,
        'page_url': page_path,
        'canonical_url': absolute_url(page_path),
        'seo_title': category_name,
        'seo_description': 'Mongona %s 技术专题，聚合相关技术文章、新闻、文档和开发实践。' % tag,
        'page_number': page_number,
        'pages': pages,
    })


def blog(request, id):
    """详情页"""
    try:
        _id = int(id)
        if not isinstance(_id, int):
            return render(request, '404.html', status=404)
    except Exception:
        logger.error(traceback.format_exc())
        return render(request, '404.html', status=404)
    try:
        article = article_queryset().get(pk=_id)  # 日志数据
        ip = request.META.get('HTTP_X_REAL_IP') or request.META.get('HTTP_X_FORWARDED_FOR') \
             or request.META.get('REMOTE_ADDR', '')
        request.ip = ip
        try:
            request_article = redis_client.get(request.ip + ':' + id)
            if not request_article:
                article.increase_article_click()  # 增加文章访问量
                redis_client.setex(request.ip + ':' + id, 24 * 3600, 1)
        except Exception:
            logger.warning('Record article click failed: %s', traceback.format_exc())
    except:
        logger.error(traceback.format_exc())
        return render(request, '404.html', status=404)

    pa = article_queryset().filter(pk__lt=_id).order_by('-pk').first()  # 前一篇日志
    na = article_queryset().filter(pk__gt=_id).order_by('pk').first()  # 下篇日志

    tags = article.article_tag.split() if article.article_tag else []  # 获得日志的tag

    return render(request, 'blog/blog.html', {
        'article': article,
        'pa': pa,
        'na': na,
        'tags': tags,
        'page_url': '/',
        'canonical_url': absolute_url('/blog/%s' % article.id),
        'seo_title': article.article_title,
        'og_type': 'article',
        'og_image': media_absolute_url(article.article_image),
        'seo_description': meta_description(article.article_synopsis, article.article_content),
        'related_articles': related_articles_for(article, tags),
        'recommended_tools': TOOL_PAGES,
    })


def article_like(request):
    if request.method.lower() == 'post':
        try:
            _id = int(request.POST.get('article_id'))
        except (TypeError, ValueError):
            return JsonResponse({'code': 1, 'state': False, 'msg': 'invalid article id'})
        is_up = request.POST.get('is_up')
        info = 'up'
        if is_up == 'true':
            Article.objects.filter(pk=_id).update(article_like=F('article_like') + 1)
        else:
            Article.objects.filter(pk=_id).update(article_down=F('article_down') + 1)
            info = 'down'
        return JsonResponse({'code': 0, 'state': True, 'msg': None, 'info': info})
    else:
        return render(request, '404.html', status=404)


def duanzi_like(request):
    if request.method.lower() == 'post':
        _id = request.POST.get('duanzi_id')
        is_up = request.POST.get('up')
        if not is_up:
            return JsonResponse({'code': 0, 'state': True, 'msg': 'nothing happend!'})
        ret = mongodb['duanzi'].update_one({'id': int(_id)}, {'$inc': {'like': 1}})
        if ret.matched_count:
            logger.info('like duanzi {} success!'.format(_id))
        return JsonResponse({'code': 0, 'state': True, 'msg': None})
    else:
        return render(request, '404.html', status=404)


def pagesHelp(page, num_pages, maxpage):
    """
    Paginator Django数据分页优化
    使数据分页列表处显示规定的页数
    :param page: 当前页码
    :param num_pages: 总页数
    :param maxpage: 列表处最多显示的页数
    :return:
    """

    if page is None:  # 首页时page=None
        p = 1
    else:
        p = int(page)
    offset = num_pages - p
    if offset <= maxpage < num_pages and p >= maxpage:
        # 假设100页 100-98=2,页尾处理
        # 结果小于规定数但是当前页大于规定页数
        return [i + 1 for i in range(num_pages - maxpage, num_pages)]

    elif num_pages > maxpage and maxpage and p < maxpage <= offset:
        # 假设100页 100-2=98，页头
        # 结果小于规定数但是当前页大于规定页数
        return [i + 1 for i in range(maxpage)]

    elif num_pages <= maxpage:
        # 假设3页  3<6，总页数很少，少于规定页数
        # 当前页码数小于规定数
        return [i + 1 for i in range(num_pages)]
    else:
        # 正常页数分配
        return [i + 1 for i in range(p - int(maxpage / 2), p + int(maxpage / 2))]


# Codex growth MVP views start
def tech_radar(request):
    page_url = '/radar/'
    q = (request.GET.get('q') or '').strip()
    active_tag = (request.GET.get('t') or '').strip()
    page_number = positive_int(request.GET.get('p'), 1)

    base_articles = article_queryset().filter(article_original='0').order_by('-article_create_time')
    filtered_articles = base_articles
    if q:
        filtered_articles = filtered_articles.filter(
            Q(article_title__contains=q) |
            Q(article_synopsis__contains=q) |
            Q(article_content__contains=q) |
            Q(article_tag__contains=q) |
            Q(article_category__category_name__contains=q)
        )
    if active_tag:
        filtered_articles = filtered_articles.filter(article_tag=active_tag)

    paginator = Paginator(filtered_articles, 10)
    try:
        contacts = paginator.page(page_number)
    except PageNotAnInteger:
        contacts = paginator.page(1)
    except EmptyPage:
        contacts = paginator.page(paginator.num_pages)
    pages = pagesHelp(page_number, paginator.num_pages, 6)

    recent_cutoff = datetime.now() - timedelta(days=1)
    source_tags = list(base_articles.exclude(article_tag='').values_list('article_tag', flat=True).distinct().order_by('article_tag')[:12])
    radar_stats = {
        'total': base_articles.count(),
        'recent': base_articles.filter(article_create_time__gte=recent_cutoff).count(),
        'ai': base_articles.filter(Q(article_tag__contains='AI') | Q(article_category__category_name__contains='AI')).count(),
    }
    radar_categories = Category.objects.filter(article__article_original='0', article__article_type='2').distinct().order_by('category_sort_id', 'category_name')[:8]

    return render(request, 'growth/radar.html', {
        'page_url': page_url,
        'canonical_url': absolute_url('/radar/'),
        'seo_title': 'Tech Radar',
        'seo_description': 'Mongona 技术雷达每日聚合 AI、开源、Python、Go、云原生、运维、安全等技术新闻和技术文档。',
        'q': q,
        'active_tag': active_tag,
        'contacts': contacts,
        'pages': pages,
        'page_number': page_number,
        'radar_stats': radar_stats,
        'source_tags': source_tags,
        'radar_categories': radar_categories,
    })


def dev_tools(request, tool_slug=None):
    active_tool = tool_by_slug(tool_slug) if tool_slug else None
    if tool_slug and not active_tool:
        return render(request, '404.html', status=404)
    page_path = '/tools/%s/' % tool_slug if active_tool else '/tools/'
    return render(request, 'growth/tools.html', {
        'page_url': page_path,
        'canonical_url': absolute_url(page_path),
        'seo_title': active_tool.get('name') if active_tool else 'Developer Tools',
        'tools': TOOL_PAGES,
        'active_tool': active_tool,
        'seo_description': meta_description(
            active_tool.get('desc') if active_tool else '',
            'Mongona 开发者工具箱，提供 JSON 格式化、JWT 解析、时间戳转换和 Cron 表达式速查。',
        ),
    })


@ensure_csrf_cookie
def sponsor(request):
    plans = [
        {
            'label': 'Starter',
            'name': '友情展示',
            'price': '99 / 月',
            'desc': '适合开源项目、个人产品、早期工具。',
            'items': ['赞助页展示', '首页侧栏入口', '保留 1 个跟踪链接'],
        },
        {
            'label': 'Growth',
            'name': '技术雷达赞助',
            'price': '299 / 月',
            'desc': '适合云服务、AI 工具、开发者产品。',
            'items': ['技术雷达页推荐位', '工具箱推荐位', '月度数据复盘'],
        },
        {
            'label': 'Pro',
            'name': '深度内容合作',
            'price': '999 / 次起',
            'desc': '适合需要评测、教程、部署实战的产品。',
            'items': ['定制文章或教程', '正文赞助声明', '长期 SEO 入口'],
        },
    ]
    services = [
        {
            'label': 'Consult',
            'name': '技术咨询',
            'price': '199 / 小时',
            'desc': 'Python、Django、Linux、部署、内网穿透、性能排查等远程咨询。',
        },
        {
            'label': 'Build',
            'name': '工具定制',
            'price': '499 起',
            'desc': '为个人或小团队做 JSON、日志、Nginx、Prompt 等轻量工具页面。',
        },
        {
            'label': 'Data',
            'name': '采集与自动化',
            'price': '999 起',
            'desc': '公开数据采集、RSS 聚合、定时任务、内容入库和合规标注。',
        },
        {
            'label': 'Review',
            'name': '项目体检',
            'price': '699 起',
            'desc': '代码结构、部署配置、缓存、CDN、接口响应和前端体验检查。',
        },
    ]
    proof_points = [
        {'name': '内容场景', 'desc': '技术雷达、工具箱、文章正文、侧栏和赞赏链路都可以承接转化。'},
        {'name': '适配产品', 'desc': '云服务、AI 工具、开发者平台、课程、招聘和开源项目。'},
        {'name': '上线方式', 'desc': '先试投或小单咨询，验证点击和反馈，再逐步做长期合作。'},
    ]
    return render(request, 'growth/sponsor.html', {
        'page_url': '/sponsor/',
        'canonical_url': absolute_url('/sponsor/'),
        'seo_title': '赞助与合作',
        'seo_description': 'Mongona 赞助与合作入口，适合云服务、AI 工具、开发者产品、课程、招聘和技术内容合作投放。',
        'plans': plans,
        'services': services,
        'proof_points': proof_points,
        'contact_email': 'ysudqfs@163.com',
    })


# Codex growth MVP views end

def page_not_found(request):
    return render(request, '404.html', status=404)


def page_error(request):
    return render(request, '500.html', status=500)


def permission_denied(request):
    return render(request, '403.html', status=403)


def robots(request):
    content = '\n'.join([
        'User-agent: *',
        'Allow: /',
        'Disallow: /debug/login/',
        'Disallow: /api/',
        'Disallow: /go/',
        'Allow: /rss.xml',
        'Allow: /feed.xml',
        'Sitemap: %s' % absolute_url('/sitemap.xml'),
        '',
    ])
    return HttpResponse(content, content_type='text/plain; charset=utf-8')


def sitemap(request):
    urls = []
    for page in STATIC_SITEMAP_PAGES:
        urls.append({
            'loc': absolute_url(page['path']),
            'lastmod': '',
            'changefreq': page['changefreq'],
            'priority': page['priority'],
        })
    for tool in TOOL_PAGES:
        urls.append({
            'loc': absolute_url('/tools/%s/' % tool['slug']),
            'lastmod': '',
            'changefreq': 'weekly',
            'priority': '0.8',
        })
    for category in Category.objects.all().order_by('category_sort_id'):
        urls.append({
            'loc': absolute_url('/?c=%s' % category.id),
            'lastmod': '',
            'changefreq': 'weekly',
            'priority': '0.6',
        })
    for tag in popular_article_tags():
        urls.append({
            'loc': absolute_url(tag_url_path(tag)),
            'lastmod': '',
            'changefreq': 'weekly',
            'priority': '0.7',
        })
    articles = Article.objects.filter(article_type='2').only('id', 'article_update_time').order_by('-article_create_time')[:2000]
    for article in articles:
        urls.append({
            'loc': absolute_url('/blog/%s' % article.id),
            'lastmod': article.article_update_time,
            'changefreq': 'weekly',
            'priority': '0.8',
        })
    return render(request, 'sitemap.html', {'urls': urls}, content_type='application/xml; charset=utf-8')
