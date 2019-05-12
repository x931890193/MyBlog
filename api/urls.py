# encoding: utf-8
"""
Create on: 2018-08-13 下午4:35
author: sato
mail: ysudqfs@163.com
life is short, you need python
"""
from api import views
from rest_framework.routers import DefaultRouter


router = DefaultRouter()  # 可以处理视图的路由器
router.register(r'poetry/search', views.PoetrySearchViewSet, base_name='ChinesePoems_search')
router.register(r'poems', views.ChinesePoemsViewSet, base_name=' 诗; 韵文; 诗一样的作品; 富有诗意的东西; ')  # 向路由器中注册视图集
router.register(r'poems_authors', views.PoemsAuthorsViewSet, base_name='诗，诗歌; 诗意，诗情; 作诗; 诗歌艺术; ')
router.register(r'poetry', views.ChinesePoetryViewSet)
router.register(r'poetry_authors', views.PoetryAuthorsViewSet)
router.register(r'areas', views.AreasViewSet, base_name='areas')
router.register(r'university', views.ChineseUniversityViewSet, base_name='大学排行榜')


urlpatterns = []
urlpatterns += router.urls


