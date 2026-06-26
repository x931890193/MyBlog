from django.contrib.syndication.views import Feed

from blog.models import Article
from blog.seo import absolute_url, meta_description


class LatestEntriesFeed(Feed):
    title = "Mongona 技术博客"
    link = absolute_url('/')
    feed_url = absolute_url('/rss.xml')
    description = "Mongona 最新技术文章、技术雷达、开发者工具和自动化实践。"

    def items(self):
        return Article.objects.filter(article_type='2').select_related(
            'article_user', 'article_category',
        ).order_by('-article_create_time')[:50]

    def item_title(self, item):
        return item.article_title

    def item_description(self, item):
        return meta_description(item.article_synopsis, item.article_content, max_length=260)

    def item_link(self, item):
        return absolute_url('/blog/%s' % item.pk)

    def item_author_name(self, item):
        if item.article_user:
            return item.article_user.user_nick_name
        return 'Mongona'

    def item_pubdate(self, item):
        return item.article_create_time

    def item_updateddate(self, item):
        return item.article_update_time

    def item_categories(self, item):
        categories = []
        if item.article_category:
            categories.append(item.article_category.category_name)
        if item.article_tag:
            categories.extend([tag for tag in item.article_tag.split() if tag])
        return categories
