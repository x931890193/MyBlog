from django.conf.urls import url, include
from django.views.static import serve
from django.conf import settings
from django.conf.urls.static import static
from MyBlog.settings import MEDIA_URL
from blog.views import blog, bloglist, robots, sitemap, articlelike

urlpatterns = [
    url(r'^$', bloglist, name=''),
    # url(r'get_lrc/?', get_lrc),
    url(r'^blog/(?P<id>\w+)$', blog, name='blog'),  # 文章id
    url(r'^blog/(?P<s>\w+)$', blog,  name='s'),  # 搜索
    url(r'^digg/like/?', articlelike, name='like'),  # 点赞
    url(r'^media/(?P<path>.*)$', serve, {"document_root": MEDIA_URL}, name='media'),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    url(r'^robots\.txt$', robots),  # robots
    url(r'^sitemap\.xml$', sitemap),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)