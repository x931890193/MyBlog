# coding=utf-8
import pickle
import random
from collections import Counter

from django.db.models import Sum, Q
from django.utils import timezone

from MyBlog.utils import redis_client
from blog.models import UserProfile, Siteinfo, Category, Article, SponsorAd
from MyBlog.env import env
from MyBlog.settings import MEDIA_URL, logger
from spider.utils import get_mongo


DEFAULT_BANNER_URL = 'https://cdn.mongona.com/banner_image/17f6bba8267f8cf8899d5ce75f820918.jpg'
SITE_INFO_CACHE_KEY = 'myblog:site_info:v2'
BANNER_CACHE_KEY = 'myblog:banner:v1'
DEFAULT_TAG_CLOUD_LIMIT = 48


def env_int(name, default):
    try:
        return int(env(name, default))
    except (TypeError, ValueError):
        return default


def get_random_banner_url():
    cache_seconds = env_int('BANNER_CACHE_SECONDS', 300)
    if cache_seconds > 0:
        try:
            cached = redis_client.get(BANNER_CACHE_KEY)
            if cached:
                return cached.decode() if isinstance(cached, bytes) else cached
        except Exception:
            pass

    try:
        collection = get_mongo()['banner']
        total = collection.count_documents({}, maxTimeMS=1000)
        if not total:
            return DEFAULT_BANNER_URL
        banner_id = random.randint(1, total)
        banner = collection.find_one({'id': banner_id}) or collection.find_one()
        banner_url = (banner or {}).get('banner_url') or DEFAULT_BANNER_URL
    except Exception as exc:
        logger.warning('Load banner from MongoDB failed: %s', exc)
        banner_url = DEFAULT_BANNER_URL

    if cache_seconds > 0:
        try:
            redis_client.setex(BANNER_CACHE_KEY, cache_seconds, banner_url)
        except Exception:
            pass
    return banner_url


def frontend_env():
    return {
        'google_ad_client': env('GOOGLE_AD_CLIENT', ''),
        'weather_app_id': env('WEATHER_APP_ID', ''),
        'weather_app_secret': env('WEATHER_APP_SECRET', ''),
        'gitalk_client_id': env('GITALK_CLIENT_ID', ''),
        'gitalk_client_secret': env('GITALK_CLIENT_SECRET', ''),
        'valine_app_id': env('VALINE_APP_ID', ''),
        'valine_app_key': env('VALINE_APP_KEY', ''),
    }


def grouped_sponsor_ads():
    grouped = {}
    try:
        now = timezone.now()
        ads = SponsorAd.objects.filter(is_active=True).filter(
            Q(start_at__isnull=True) | Q(start_at__lte=now),
            Q(end_at__isnull=True) | Q(end_at__gte=now),
        ).order_by('placement', '-priority', '-time_create')[:20]
        for ad in ads:
            grouped.setdefault(ad.placement, []).append(ad)
    except Exception as exc:
        logger.warning('Load sponsor ads failed: %s', exc)
    return grouped


def popular_site_tags():
    limit = env_int('TAG_CLOUD_LIMIT', DEFAULT_TAG_CLOUD_LIMIT)
    if limit <= 0:
        return []
    counter = Counter()
    tag_values = Article.objects.filter(article_type='2').exclude(article_tag='') \
        .values_list('article_tag', flat=True).order_by('-article_create_time')[:2000]
    for value in tag_values:
        counter.update(tag for tag in (value or '').split() if tag)
    return [tag for tag, count in counter.most_common(limit)]


def build_site_info():
    userinfo = UserProfile.objects.get(id=1)  # 站长资料
    siteinfo = Siteinfo.objects.get(pk=1)  # 获取站点信息
    categorys = list(Category.objects.filter().order_by('category_sort_id'))  # 获取所有分类
    base_query = Article.objects.filter(article_type=2)
    hot_articles = list(base_query.order_by('-article_click')[:10])  # 获取热门文章
    ac_count = base_query.count()  # 获得文章数量
    dates = list(Article.objects.datetimes('article_create_time', 'month', order='DESC', tzinfo='Asia/Shanghai'))
    tags = popular_site_tags()
    ac_click = base_query.aggregate(total=Sum('article_click')).get('total') or 0
    tagcss = ['am-radius', 'am-square', 'am-badge-primary', 'am-badge-secondary',
              'am-badge-success', 'am-badge-warning', 'am-badge-danger']

    return {'userinfo': userinfo, 'siteinfo': siteinfo, 'categorys': categorys,
            'dates': dates, 'alltags': tags, 'tagcss': tagcss,
            'hot_articles': hot_articles, 'ac_count': ac_count, 'ac_click': ac_click,
            'sponsor_ads': grouped_sponsor_ads(), 'MEDIA_URL': MEDIA_URL}


def load_cached_site_info(force=None):
    cache_seconds = env_int('SITE_INFO_CACHE_SECONDS', 60)
    if force or cache_seconds <= 0:
        return build_site_info()

    try:
        cached = redis_client.get(SITE_INFO_CACHE_KEY)
        if cached:
            return pickle.loads(cached)
    except Exception as exc:
        logger.warning('Load site info cache failed: %s', exc)

    data = build_site_info()
    try:
        redis_client.setex(SITE_INFO_CACHE_KEY, cache_seconds, pickle.dumps(data))
    except Exception as exc:
        logger.warning('Save site info cache failed: %s', exc)
    return data


def site_info(request, force=None):
    data = load_cached_site_info(force=force).copy()
    data['alltags'] = list(data.get('alltags') or [])
    data['banner'] = get_random_banner_url()
    data.update(frontend_env())
    return data
