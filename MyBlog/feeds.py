from django.contrib.syndication.views import Feed
from django.urls import reverse

from blog.models import Article


class LatestEntriesFeed(Feed):
    title = "mongona news"
    link = "/rss"
    description = "mongona 站点文章更新。"

    # 数据
    def items(self):
        return Article.objects.order_by('-article_create_time')

    # 标题
    def item_title(self, item):
        return item.article_title

    # 简介
    def item_description(self, item):
        return item.article_synopsis

    # 生成连接
    def item_link(self, item):
        return reverse('blog', args=[item.pk])
