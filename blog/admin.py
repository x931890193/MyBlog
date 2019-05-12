# coding=utf-8
from django.contrib import admin
from django.utils.safestring import mark_safe

from MyBlog.context_processor import site_info
from MyBlog.utils import redis_client
from .models import UserProfile, Article, Category, Siteinfo, Acimage, ImageCategory


class UserProfileAdmin(admin.ModelAdmin):
    """用来显示用户相关"""
    list_display = ('username', 'user_nick_name', 'email', 'user_gender', 'user_mobile', 'user_address')
    # 过滤器设置
    list_filter = ('username', 'user_nick_name', 'email')
    # 搜索
    search_fields = ('username', 'user_nick_name', 'email')

    def save_model(self, request, obj, form, change):
        """
       重写保存方法, 把站点信息写入redis
        """
        super().save_model(request, obj, form, change)
        redis_client.delete('site_info')
        site_info(request, force=True)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'category_detail', 'category_sort_id', 'category_icon')
    # 过滤器设置
    list_filter = ('category_name', 'category_sort_id')


class ArticleAdmin(admin.ModelAdmin):
    """文章字段"""
    list_display = (
        'article_title', 'article_user', 'article_category', 'article_type', 'article_up', 'article_support', 'article_like',
        'article_click')

    list_per_page = 15
    # 筛选器
    list_filter = ('article_category', 'article_create_time')  # 过滤器
    search_fields = ('article_title',)  # 搜索字段
    date_hierarchy = 'article_create_time'  # 详细时间分层筛选

    def save_model(self, request, obj, form, change):
        """
       重写保存方法, 把站点信息写入redis
        """
        super().save_model(request, obj, form, change)
        redis_client.delete('site_info')
        site_info(request, force=True)


class SiteinfoAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'site_user', 'site_detail')

    def save_model(self, request, obj, form, change):
        """
       重写保存方法, 把站点信息写入redis
        """
        super().save_model(request, obj, form, change)
        redis_client.delete('site_info')
        site_info(request, force=True)

class AcimageAdmin(admin.ModelAdmin):
    list_display = ('image_title', 'image_detail', 'image_url', 'image_data')
    readonly_fields = ('image_data', 'image_url',)  # 必须加这行 否则访问编辑页面会报错

    def image_url(self, obj):
        return mark_safe('<a href="%s">右键复制图片地址</a>' % obj.image_path.url)

    def image_data(self, obj):
        img = mark_safe('<img src="%s" width="100px" />' % obj.image_path.url)
        return img

    # 页面显示的字段名称
    image_data.short_description = '图片'
    image_url.short_description = '图片地址'


class ImageCategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'category_detail', 'category_icon', 'category_sort_id')


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Siteinfo, SiteinfoAdmin)
admin.site.register(Acimage, AcimageAdmin)
admin.site.register(ImageCategory, ImageCategoryAdmin)


admin.site.site_title="你会不会突然的出现"
admin.site.site_header="Mongona 后台管理系统"
admin.site.index_title="Mongona 后台管理"