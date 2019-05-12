from django.contrib import admin
from django.conf.urls import url, include
from MyBlog.feeds import LatestEntriesFeed


urlpatterns = [
    url(r'^', include('blog.urls')),
    url(r'^debug/login/', admin.site.urls),
    url(r'^rss/?$', LatestEntriesFeed(), name='rss'),  # rss
    url(r'^api/', include('api.urls')),
]
