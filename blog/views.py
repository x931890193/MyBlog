# coding=utf-8
import json
import random
import traceback
from datetime import datetime

import requests
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger  # 翻页相关模块
from django.db.models import Q  # 模糊查询多个字段使用
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from urllib3.exceptions import InsecureRequestWarning

from MyBlog.settings import logger
from .forms import Searchform, Tagform
from .models import Article, Acimage, Category
from MyBlog.utils import get_video_curl, redis_client


def bloglist(request):
    page_url = request.get_full_path()
    c = request.GET.get('c', '')  # 分类
    if c:
        try:
            c = int(c)
        except ValueError:
            return render(request, '404.html')
        if c == 4:
            images = Acimage.objects.all().order_by('-time_create')
            return render(request, 'gallery/image.html',
                          {'images': images, 'page_url': page_url, 'category_name': "Gallery"})
        elif c == 5:
            hotcomment_url = 'https://api.comments.hk/?random={}'.format(random.uniform(0, 1))
            comment_data = dict()
            try:
                hotcomment = requests.get(url=hotcomment_url, verify=False)
                if hotcomment.status_code not in (200, 201):
                    logger.error('get hotcomment net worker error, {}'.format(hotcomment.text))
                comment_data = hotcomment.json()
                song_id = comment_data.get('song_id')
                lrc_data = get_lrc(song_id)
                format_lrc = lrc_data.get('lrc').split('\n')
                logger.info(format_lrc)
                pretty_lrc = [lrc[lrc.index(']')+1:] for lrc in format_lrc if lrc]
                api_count_url = 'https://api.comments.hk/count?random={}'.format(random.uniform(0, 1))
                api_count = requests.get(url=api_count_url, verify=False)
                api_count_data = api_count.json()
                comment_data.update(api_count_data)
                comment_data.update({'category_name': "life", 'format_lrc': format_lrc, 'pretty_lrc': pretty_lrc})
                logger.info(comment_data)
            except InsecureRequestWarning:
                pass
            except Exception as e:
                traceback.print_exc()
                logger.error(e)
                data_byte = redis_client.hget('song', random.choice(['当真', 'Something Just Like This', '曾经的你']))
                comment_data = json.loads(data_byte.decode())
                return render(request, 'life/life.html', {'data': comment_data})
            song_name = comment_data.get('title')
            song_str = json.dumps(comment_data)
            redis_client.hset('song', song_name, song_str)
            return render(request, 'life/life.html', {'data': comment_data})

    # 获取当前页码，用来控制翻页中当前页码的class="{% if p == page_number %}am-active {% endif %}"
    page_number = int(request.GET.get('p', '1'))
    s = ''  # 搜索关键字
    t = ''  # TAG关键字
    d = request.GET.get('d', '')  # 默认文章归档
    form = ''
    if request.method == 'GET':
        form_s = Searchform(request.GET)
        form_t = Tagform(request.GET)

        if form_s.is_valid():
            s = request.GET.get('s')
        if form_t.is_valid():
            t = request.GET.get('t')
    category_name = '富强，民主，文明，和谐，自由，平等，公正，法治，爱国，敬业，诚信，友善。'
    if c:
        # 分类页
        articles = Article.objects.filter(article_category=c, article_type='2').order_by('-article_create_time')
        try:
            category_name = Category.objects.get(pk=c).category_detail
        except Exception as e:
            traceback.print_exc()
            logger.error(e)
    elif s:
        # 搜索结果
        articles = Article.objects.filter(Q(article_title__contains=s) | Q(article_content__contains=s),
                                          article_type='2').order_by('-article_create_time')
    elif t:
        # 标签页搜索结果
        articles = Article.objects.filter(article_tag__contains=t, article_type='2').order_by('-article_create_time')

    elif d:
        # 文章归档 创建时间对象，然后取年，月，利用filter来取相关时间的日志。
        md = datetime.strptime(d, "%Y-%m")
        articles = Article.objects.filter(article_create_time__year=md.year, article_create_time__month=md.month,
                                          article_type='2').order_by('-article_create_time')
    else:
        # 否则全部文章
        articles = Article.objects.filter(article_type='2').order_by('-article_create_time')

    paginator = Paginator(articles, 5)  # 第二个参数是每页显示的数量
    page = request.GET.get('p')  # 获取URL参数中的page number
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:  # 若不是整数则跳到第一页
        contacts = paginator.page(1)
    except EmptyPage:  # 若超过了则最后一页
        contacts = paginator.page(paginator.num_pages)
    # 优化数据翻页
    pages = pagesHelp(page, paginator.num_pages, 6)

    return render(request, 'blog/list.html', {'articles': articles,
                                              'contacts': contacts,
                                              'category_name': category_name,
                                              'c': c,
                                              's': s,
                                              'd': d,
                                              't': t,
                                              'page_url': page_url,
                                              'page_number': page_number,
                                              'pages': pages})


def blog(request, id):
    """详情页"""
    try:
        _id = int(id)
        if not isinstance(_id, int):
            return render(request, '404.html')
    except Exception:
        logger.error(traceback.format_exc())
    try:
        article = Article.objects.get(pk=id, article_type='2')  # 日志数据
        article.increase_article_click()  # 增加文章访问量
    except:
        logger.error(traceback.format_exc())
        return render(request, '404.html')

    pa = Article.objects.filter(pk__lte=_id - 1, article_type='2').last()  # 前一篇日志
    na = Article.objects.filter(pk__gte=_id + 1, article_type='2').first()  # 下篇日志

    tags = article.article_tag.split()  # 获得日志的tag

    return render(request, 'blog/blog.html', {'article': article, 'pa': pa, 'na': na, 'tags': tags})


def articlelike(request):
    if request.method.lower() == 'post':
        _id = request.POST.get('article_id')
        is_up = request.POST.get('is_up')
        article = Article.objects.get(pk=int(_id))
        if is_up == 'true':
            article.article_like += 1
        else:
            article.article_down += 1
        article.save()
        return JsonResponse({'code': 0, 'state': True, 'msg': None})
    else:
        return render(request, '404.html')


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
    # print(num_pages,p,maxpage)
    offset = num_pages - p
    if num_pages > maxpage and offset <= maxpage and p >= maxpage:
        # 假设100页 100-98=2,页尾处理
        # 结果小于规定数但是当前页大于规定页数
        # print("结果小于规定数但是当前页大于规定页数",[i + 1 for i in range(num_pages - maxpage, num_pages)])
        return [i + 1 for i in range(num_pages - maxpage, num_pages)]

    elif num_pages > maxpage and offset >= maxpage and p <= maxpage:
        # 假设100页 100-2=98，页头
        # 结果小于规定数但是当前页大于规定页数
        # print("结果小于规定数但是当前页大于规定页数",[i + 1 for i in range(maxpage)])
        return [i + 1 for i in range(maxpage)]

    elif num_pages <= maxpage:
        # 假设3页  3<6，总页数很少，少于规定页数
        # 当前页码数小于规定数
        # print("当前页码数小于规定数",[i + 1 for i in range(num_pages)])
        return [i + 1 for i in range(num_pages)]
    else:
        # 正常页数分配
        # print("正常页数分配",[i + 1 for i in range(p - int(maxpage / 2), p + int(maxpage / 2))])
        return [i + 1 for i in range(p - int(maxpage / 2), p + int(maxpage / 2))]


def page_not_found(request):
    return render(request, '404.html')


def page_error(request):
    return render(request, '500.html')


def permission_denied(request):
    return render(request, '403.html')


def robots(request):
    return HttpResponse('User-agent: *<br />Sitemap: /sitemap.xml')


def sitemap(request):
    articles = Article.objects.filter(article_type='2').order_by('-article_create_time')
    return render(request, 'sitemap.html', {'articles': articles}, content_type="text/xml")


def get_lrc(song_id):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0'}
    url = 'http://music.163.com/api/song/media?id={}'.format(song_id)
    res = requests.get(url=url, headers=headers)
    if res.status_code not in (200, 201):
        data = {'lrc': '[00:20.010] 获取歌词失败！'}
    else:
        json_data = json.loads(res.text)
        data = {'lrc': json_data.get('lyric', "[00:20.010] 暂无歌词～")}
        # data['lrc'] = data['lrc'].replace('\n', '')
        data['lrc'] = data['lrc'].replace('\r\n', '\n')
        data['lrc'] = data['lrc'].replace('\n\n', '\n')
        data['lrc'] = data['lrc'].replace('\r', '\n')

        lrc = data['lrc'].split('\n')
        data['lrc'] = '\n'.join(l for l in lrc if all(l.split(']')))
    # logger.info(data)
    return data

