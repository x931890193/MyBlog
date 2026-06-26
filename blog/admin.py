# coding=utf-8
from django.contrib import admin
from django.utils.safestring import mark_safe
import requests
from MyBlog.context_processor import site_info
from MyBlog.env import env
from MyBlog.utils import redis_client
from .models import (
    UserProfile, Article, Category, Siteinfo, Acimage, ImageCategory,
    PerformanceMetric, SponsorLead, SponsorAd,
)
from .seo import absolute_url, site_base_url


SITE_INFO_CACHE_KEY = 'myblog:site_info:v2'
PAGE_CACHE_PATTERN = 'page_cache_v1*'


def clear_site_info_cache():
    try:
        redis_client.delete(SITE_INFO_CACHE_KEY)
    except Exception:
        pass


def clear_page_cache():
    try:
        keys = list(redis_client.scan_iter(PAGE_CACHE_PATTERN))
        if keys:
            redis_client.delete(*keys)
    except Exception:
        pass


def clear_commercial_cache():
    clear_site_info_cache()
    clear_page_cache()


class UserProfileAdmin(admin.ModelAdmin):
    """用来显示用户相关"""
    list_display = ('username', 'user_nick_name', 'email', 'user_gender', 'user_mobile', 'user_address')
    # 过滤器设置
    list_filter = ('username', 'user_nick_name', 'email')
    # 搜索
    search_fields = ('username', 'user_nick_name', 'email')

    def save_model(self, request, obj, form, change):
        """
       重写保存方法
        """
        super().save_model(request, obj, form, change)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'category_detail', 'category_sort_id', 'category_icon')
    # 过滤器设置
    list_filter = ('category_name', 'category_sort_id')


class ArticleAdmin(admin.ModelAdmin):
    """文章"""
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
       重写保存方法,
        """
        super().save_model(request, obj, form, change)
        baidu_token = env('BAIDU_PUSH_TOKEN', '')
        if baidu_token:
            baidu_url = 'http://data.zz.baidu.com/urls?site={site}&token={token}'.format(
                site=site_base_url(),
                token=baidu_token,
            )
            try:
                res = requests.post(url=baidu_url, data='\n'.join([absolute_url('/blog/{}'.format(obj.id))]), timeout=5)
                print(res.text)
            except Exception:
                pass


class SiteinfoAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'site_user', 'site_detail')

    def save_model(self, request, obj, form, change):
        """
       重写保存方法,
        """
        super().save_model(request, obj, form, change)


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


class SponsorLeadAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'contact', 'demand_type', 'budget', 'status', 'source_path', 'time_create')
    list_filter = ('status', 'demand_type', 'budget', 'time_create')
    search_fields = ('name', 'company', 'contact', 'message', 'source_path')
    readonly_fields = ('ip', 'referer', 'user_agent', 'source_path', 'time_create', 'time_modify')
    list_editable = ('status',)
    list_per_page = 20


class SponsorAdAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'sponsor_name', 'placement', 'priority', 'is_active',
        'impression_count', 'click_count', 'dismiss_count', 'ctr_rate', 'start_at', 'end_at',
    )
    list_filter = ('placement', 'is_active', 'start_at', 'end_at')
    search_fields = ('title', 'sponsor_name', 'description', 'target_url', 'image_url')
    readonly_fields = ('impression_count', 'click_count', 'dismiss_count', 'ctr_rate', 'time_create', 'time_modify')
    list_editable = ('priority', 'is_active')
    list_per_page = 20

    def ctr_rate(self, obj):
        if not obj.impression_count:
            return '0.00%'
        return '%.2f%%' % (obj.click_count * 100.0 / obj.impression_count)
    ctr_rate.short_description = '点击率'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        clear_commercial_cache()

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        clear_commercial_cache()

    def delete_queryset(self, request, queryset):
        super().delete_queryset(request, queryset)
        clear_commercial_cache()


class PerformanceMetricAdmin(admin.ModelAdmin):
    list_display = (
        'time_create', 'method', 'status_code', 'duration_badge', 'db_query_count',
        'cache_status', 'is_slow', 'path_short',
    )
    list_filter = ('is_slow', 'status_code', 'method', 'cache_status', 'time_create')
    search_fields = ('path', 'referer', 'user_agent', 'ip')
    readonly_fields = (
        'method', 'path', 'path_hash', 'status_code', 'duration_ms', 'db_query_count',
        'cache_status', 'is_slow', 'ip', 'referer', 'user_agent', 'time_create',
    )
    date_hierarchy = 'time_create'
    list_per_page = 50

    def has_add_permission(self, request):
        return False

    def duration_badge(self, obj):
        color = '#34c759'
        if obj.duration_ms >= 1000:
            color = '#ff3b30'
        elif obj.duration_ms >= 500:
            color = '#ff9500'
        return mark_safe('<strong style="color:%s">%sms</strong>' % (color, obj.duration_ms))
    duration_badge.short_description = '耗时'
    duration_badge.admin_order_field = 'duration_ms'

    def path_short(self, obj):
        path = obj.path or ''
        return path if len(path) <= 96 else path[:93] + '...'
    path_short.short_description = '请求路径'


admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Siteinfo, SiteinfoAdmin)
admin.site.register(Acimage, AcimageAdmin)
admin.site.register(ImageCategory, ImageCategoryAdmin)
admin.site.register(PerformanceMetric, PerformanceMetricAdmin)
admin.site.register(SponsorLead, SponsorLeadAdmin)
admin.site.register(SponsorAd, SponsorAdAdmin)


admin.site.site_title="你会不会突然的出现"
admin.site.site_header="Mongona 后台管理系统"
admin.site.index_title="Mongona 后台管理"
