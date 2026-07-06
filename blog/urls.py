from django.conf.urls import url, include
from django.views.static import serve
from django.conf import settings
from django.conf.urls.static import static
from MyBlog.settings import MEDIA_URL
from blog.views import blog, bloglist, robots, sitemap, article_like, duanzi_like, tech_radar, dev_tools, sponsor, random_music_api, site_assistant_api, sponsor_lead_api, sponsor_ad_redirect, sponsor_ad_event_api, tag_landing, weather_api

urlpatterns = [
    url(r'^$', bloglist, name=''),
    url(r'^radar/?$', tech_radar, name='radar'),
    url(r'^tools/?$', dev_tools, name='tools'),
    url(r'^tools/(?P<tool_slug>[a-z0-9-]+)/?$', dev_tools, name='tool_detail'),
    url(r'^sponsor/?$', sponsor, name='sponsor'),
    url(r'^tag/(?P<tag>[^/]+)/?$', tag_landing, name='tag_landing'),
    url(r'^go/(?P<ad_id>\d+)/?$', sponsor_ad_redirect, name='sponsor_ad_redirect'),
    url(r'^api/random-music/?$', random_music_api, name='random_music_api'),
    url(r'^api/site-assistant/?$', site_assistant_api, name='site_assistant_api'),
    url(r'^api/weather/?$', weather_api, name='weather_api'),
    url(r'^api/sponsor-lead/?$', sponsor_lead_api, name='sponsor_lead_api'),
    url(r'^api/sponsor-ad-event/?$', sponsor_ad_event_api, name='sponsor_ad_event_api'),
    url(r'^blog/(?P<id>\w+)$', blog, name='blog'),  # 文章id
    url(r'^blog/(?P<s>\w+)$', blog,  name='s'),  # 搜索
    url(r'^digg/like/?', article_like, name='like'),  # 点赞
    url(r'^duanzi/like/?', duanzi_like, name='duanzi_like'),  # 点赞
    url(r'^media/(?P<path>.*)$', serve, {"document_root": MEDIA_URL}, name='media'),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    url(r'^robots\.txt$', robots),  # robots
    url(r'^sitemap\.xml$', sitemap),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
