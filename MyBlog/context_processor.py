# coding=utf-8
import pickle
import datetime
from random import shuffle

from MyBlog.utils import redis_client
from blog.models import UserProfile, Siteinfo, Category, Article
from MyBlog.settings import MEDIA_URL, logger


def site_info(request, force=None):
    site_info = redis_client.hgetall('site_info')
    if force or not site_info:
        userinfo = UserProfile.objects.get(id=1)# 站长资料
        siteinfo = Siteinfo.objects.get(pk=1)  # 获取站点信息
        categorys = Category.objects.all().order_by('category_sort_id')  # 获取所有分类
        hot_articles = Article.objects.all().order_by('-article_click')[:10]  # 获取热门文章
        ac_count = Article.objects.count()  # 获得文章数量
        dates = Article.objects.datetimes('article_create_time', 'month', order='DESC', tzinfo='Asia/Shanghai')
        # 获取文章标签
        tag_list = ' '.join(list(Article.objects.filter(article_type='2').values_list("article_tag", flat=True).distinct()))
        tags = list(set(tag_list.split(' ')))

        redis_client.hset('site_info', 'userinfo', pickle.dumps(userinfo))
        redis_client.hset('site_info', 'siteinfo', pickle.dumps(siteinfo))
        redis_client.hset('site_info', 'categorys', pickle.dumps(categorys))
        redis_client.hset('site_info', 'hot_articles', pickle.dumps(hot_articles))
        redis_client.hset('site_info', 'ac_count', pickle.dumps(ac_count))
        redis_client.hset('site_info', 'dates', pickle.dumps(dates))
        redis_client.hset('site_info', 'tags', pickle.dumps(tags))
        logger.info("{} data from mysql".format(datetime.datetime.now()))
    else:
        userinfo = pickle.loads(site_info.get(b'userinfo'))
        siteinfo = pickle.loads(site_info.get(b'siteinfo'))
        categorys = pickle.loads(site_info.get(b'categorys'))
        hot_articles = pickle.loads(site_info.get(b'hot_articles'))
        ac_count = pickle.loads(site_info.get(b'ac_count'))
        dates = pickle.loads(site_info.get(b'dates'))
        tags = pickle.loads(site_info.get(b'tags'))
        logger.info("{} data from redis".format(datetime.datetime.now()))

    acs = list(Article.objects.all())
    ac_click = 0
    for ac in acs:
        ac_click += int(ac.article_click)

    shuffle(tags)

    tagcss = ['am-radius', 'am-square', 'am-badge-primary', 'am-badge-secondary',
              'am-badge-success', 'am-badge-warning','am-badge-danger']

    return {'userinfo': userinfo, 'siteinfo': siteinfo, 'categorys': categorys,
            'dates': dates, 'alltags': tags, 'tagcss': tagcss,
            'hot_articles': hot_articles, 'ac_count': ac_count, 'ac_click': ac_click,
            'MEDIA_URL': MEDIA_URL}
