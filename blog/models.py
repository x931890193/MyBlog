# coding=utf-8
from ckeditor_uploader.fields import RichTextUploadingField

from django.contrib.auth.models import AbstractUser
from django.db import models


class UserProfile(AbstractUser):
    """继承django系统自带的user创建用户表，
    """
    user_nick_name = models.CharField(max_length=24, verbose_name='用户昵称', default="")
    user_gender = models.CharField(max_length=10, choices=(("1", "男"), ("0", "女")), default="1", verbose_name='性别选择')
    user_birday = models.DateField(verbose_name='用户生日', null=True, blank=True)
    user_mobile = models.CharField(max_length=11, null=True, blank=True, verbose_name='电话号码')
    user_address = models.CharField(max_length=200, verbose_name='用户地址', default='')
    user_detail = models.CharField(max_length=200, verbose_name='人简介', default='')
    user_image = models.ImageField(upload_to='upload/image/user/%Y/%m', default='',
                                   max_length=100,
                                   verbose_name="用户头像")

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.username


class Category(models.Model):
    """blog 分类"""
    category_name = models.CharField(max_length=20, verbose_name='分类名称', default='')
    category_detail = models.CharField(max_length=100, verbose_name='分类介绍', default='')
    category_icon = models.CharField(max_length=100, verbose_name='分类图标', default='')
    category_sort_id = models.IntegerField(verbose_name='分类排序', default=1, db_index=True)

    class Meta:
        verbose_name = '博客分类'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.category_name


class Article(models.Model):
    """博客文章"""
    article_title = models.CharField(max_length=180, verbose_name='日志标题', default='')
    article_synopsis = models.TextField(verbose_name='日志简介', default='')
    article_image = models.ImageField(upload_to='upload/image/article/%Y/%m', default='',
                                      max_length=100, verbose_name='文章配图', null=True, blank=True)
    article_user = models.ForeignKey(UserProfile, verbose_name='文章作者', null=True, blank=True)
    article_category = models.ForeignKey(Category, verbose_name='所属分类', null=True, blank=True)
    article_tag = models.CharField(max_length=120, verbose_name='日志标签', default='')
    article_content = RichTextUploadingField(verbose_name='博客正文', default='')
    article_type = models.CharField(max_length=10, choices=(('0', '草稿'), ('1', '软删除'), ('2', '正常')), default='2',
                                    verbose_name='文章类别', db_index=True)
    article_original = models.CharField(max_length=10, choices=(('1', '原创'), ('0', '转载')), default='1',
                                        verbose_name='是否原创')
    article_click = models.PositiveIntegerField(verbose_name='文章点击量', default=0, db_index=True)
    article_up = models.CharField(max_length=10, choices=(('1', '置顶'), ('0', '取消置顶')), default='1',
                                  verbose_name='文章置顶')
    article_support = models.CharField(max_length=10, choices=(("1", '推荐'), ('0', '取消推荐')), default='1',
                                       verbose_name="文章推荐")
    article_like = models.IntegerField(verbose_name='顶', default=0)
    article_down = models.IntegerField(verbose_name='踩', default=0)
    article_create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True, db_index=True)
    article_update_time = models.DateTimeField(verbose_name='更新时间', auto_now=True)

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.article_title

    def increase_article_click(self):
        """文章点击量"""
        self.article_click += 1
        self.save(update_fields=['article_click'])


class Siteinfo(models.Model):
    """站点信息"""
    site_name = models.CharField(max_length=20, verbose_name='站点名称', default='')
    site_detail = models.CharField(max_length=100, verbose_name='站点介绍', default='')
    site_user = models.ForeignKey(UserProfile, verbose_name='管理员', null=True, blank=True)
    site_logo = models.ImageField(upload_to='upload/image/site/', default='', max_length=100,
                                  verbose_name='站点logo')
    site_topimage = models.ImageField(upload_to='upload/image/site/', default='', max_length=100,
                                      verbose_name="顶部大图")
    site_powered = models.TextField(verbose_name='Powered By', default='')
    site_links = models.TextField(verbose_name='links', default='')
    site_contact = models.TextField(verbose_name='contact me', default='')
    site_footer = models.TextField(verbose_name='站点底部代码', default='')
    site_changyan = models.TextField(verbose_name='文章底部广告代码', default='')

    class Meta:
        verbose_name = '网站信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.site_name


class ImageCategory(models.Model):
    """图片 分类"""
    category_name = models.CharField(max_length=20, verbose_name='分类名称', default='')
    category_detail = models.CharField(max_length=100, verbose_name='分类介绍', default='')
    category_icon = models.CharField(max_length=100, verbose_name='分类图标', default='')
    category_sort_id = models.IntegerField(verbose_name='分类排序', default=1)

    class Meta:
        verbose_name = '图片分类'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.category_name


class Acimage(models.Model):
    """相册"""
    image_title = models.CharField(max_length=20, verbose_name='图片标题', default='')
    image_detail = models.CharField(max_length=200, verbose_name='图片简介', default='')
    image_path = models.ImageField(upload_to='upload/image/%Y/%m', default='', max_length=100,  verbose_name='图片路径')
    image_category = models.ForeignKey(ImageCategory, max_length=20, verbose_name='图片分类', default=1)
    time_create = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    time_modify = models.DateTimeField(verbose_name='修改时间', auto_now=True)

    class Meta:
        verbose_name = '网站相册'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.image_title


class RequestInfo(models.Model):
    """访客信息"""
    request_ip = models.GenericIPAddressField(default='')
    request_region = models.CharField(max_length=128, default='')
    request_ua = models.CharField(max_length=512, default='')
    request_path = models.CharField(max_length=512, default='')
    request_referer = models.CharField(max_length=2048, default='')  # referer
    request_times = models.IntegerField(default=0)   # 访问次数
    time_create = models.DateTimeField(auto_now_add=True)
    time_modify = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '访客信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.request_region + ':' + self.request_ip


class PerformanceMetric(models.Model):
    """页面/接口响应性能记录"""
    method = models.CharField(max_length=8, verbose_name='请求方法', default='GET', db_index=True)
    path = models.CharField(max_length=512, verbose_name='请求路径', default='')
    path_hash = models.CharField(max_length=32, verbose_name='路径指纹', default='', db_index=True)
    status_code = models.PositiveIntegerField(verbose_name='状态码', default=200, db_index=True)
    duration_ms = models.PositiveIntegerField(verbose_name='响应耗时(ms)', default=0, db_index=True)
    db_query_count = models.PositiveIntegerField(verbose_name='DB 查询数', default=0)
    cache_status = models.CharField(max_length=16, verbose_name='页面缓存', default='skip', db_index=True)
    is_slow = models.BooleanField(verbose_name='慢请求', default=False, db_index=True)
    ip = models.GenericIPAddressField(verbose_name='访问 IP', null=True, blank=True)
    referer = models.CharField(max_length=1024, verbose_name='来路', default='', blank=True)
    user_agent = models.CharField(max_length=512, verbose_name='User Agent', default='', blank=True)
    time_create = models.DateTimeField(verbose_name='记录时间', auto_now_add=True, db_index=True)

    class Meta:
        ordering = ('-time_create',)
        verbose_name = '性能监控'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s %sms %s' % (self.path, self.duration_ms, self.status_code)


class SponsorLead(models.Model):
    """合作/赞助/定制需求线索"""
    DEMAND_CHOICES = (
        ('sponsor', '赞助投放'),
        ('custom_tool', '工具定制'),
        ('consult', '技术咨询'),
        ('content', '内容合作'),
        ('automation', '采集与自动化'),
        ('other', '其他需求'),
    )
    BUDGET_CHOICES = (
        ('unknown', '暂未确定'),
        ('lt_1k', '1000 元以内'),
        ('1k_5k', '1000-5000 元'),
        ('5k_20k', '5000-20000 元'),
        ('gt_20k', '20000 元以上'),
    )
    STATUS_CHOICES = (
        ('new', '新线索'),
        ('contacted', '已联系'),
        ('qualified', '有效机会'),
        ('won', '已成交'),
        ('lost', '已关闭'),
    )

    name = models.CharField(max_length=80, verbose_name='姓名/称呼')
    company = models.CharField(max_length=120, verbose_name='公司/产品', default='', blank=True)
    contact = models.CharField(max_length=160, verbose_name='联系方式')
    demand_type = models.CharField(max_length=32, choices=DEMAND_CHOICES, default='sponsor', verbose_name='需求类型')
    budget = models.CharField(max_length=32, choices=BUDGET_CHOICES, default='unknown', verbose_name='预算')
    message = models.TextField(verbose_name='需求描述', default='', blank=True)
    source_path = models.CharField(max_length=512, verbose_name='提交来源', default='', blank=True)
    referer = models.CharField(max_length=1024, verbose_name='来路', default='', blank=True)
    user_agent = models.CharField(max_length=512, verbose_name='User Agent', default='', blank=True)
    ip = models.GenericIPAddressField(verbose_name='访问 IP', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', db_index=True, verbose_name='跟进状态')
    note = models.TextField(verbose_name='跟进备注', default='', blank=True)
    time_create = models.DateTimeField(verbose_name='提交时间', auto_now_add=True, db_index=True)
    time_modify = models.DateTimeField(verbose_name='更新时间', auto_now=True)

    class Meta:
        ordering = ('-time_create',)
        verbose_name = '合作线索'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s - %s' % (self.name, self.contact)


class SponsorAd(models.Model):
    """可售广告/合作位"""
    PLACEMENT_CHOICES = (
        ('sidebar', '侧栏商业位'),
        ('article_bottom', '文章底部'),
        ('tools', '工具页'),
        ('radar', '技术雷达'),
        ('sponsor', '赞助页'),
    )

    title = models.CharField(max_length=120, verbose_name='广告标题')
    sponsor_name = models.CharField(max_length=120, verbose_name='赞助方', default='', blank=True)
    description = models.CharField(max_length=240, verbose_name='广告描述', default='', blank=True)
    target_url = models.URLField(max_length=500, verbose_name='目标链接')
    image_url = models.URLField(max_length=500, verbose_name='广告图片', default='', blank=True)
    cta_text = models.CharField(max_length=40, verbose_name='按钮文案', default='了解详情')
    placement = models.CharField(max_length=32, choices=PLACEMENT_CHOICES, default='sidebar',
                                 verbose_name='展示位置', db_index=True)
    priority = models.IntegerField(verbose_name='排序权重', default=0, db_index=True)
    is_active = models.BooleanField(verbose_name='启用', default=True, db_index=True)
    start_at = models.DateTimeField(verbose_name='开始时间', null=True, blank=True)
    end_at = models.DateTimeField(verbose_name='结束时间', null=True, blank=True)
    impression_count = models.PositiveIntegerField(verbose_name='曝光数', default=0)
    dismiss_count = models.PositiveIntegerField(verbose_name='关闭数', default=0)
    click_count = models.PositiveIntegerField(verbose_name='点击数', default=0)
    time_create = models.DateTimeField(verbose_name='创建时间', auto_now_add=True, db_index=True)
    time_modify = models.DateTimeField(verbose_name='更新时间', auto_now=True)

    class Meta:
        ordering = ('placement', '-priority', '-time_create')
        verbose_name = '赞助广告位'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title
