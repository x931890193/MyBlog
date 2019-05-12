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
    category_sort_id = models.IntegerField(verbose_name='分类排序', default=1)

    class Meta:
        verbose_name = '博客分类'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.category_name


class Article(models.Model):
    """博客文章"""
    article_title = models.CharField(max_length=50, verbose_name='日志标题', default='')
    article_synopsis = models.TextField(verbose_name='日志简介', default='')
    article_image = models.ImageField(upload_to='upload/image/article/%Y/%m', default='',
                                      max_length=100, verbose_name='文章配图', null=True, blank=True)
    article_user = models.ForeignKey(UserProfile, verbose_name='文章作者', null=True, blank=True)
    article_category = models.ForeignKey(Category, verbose_name='所属分类', null=True, blank=True)
    article_tag = models.CharField(max_length=50, verbose_name='日志标签', default='')
    article_content = RichTextUploadingField(verbose_name='博客正文', default='')
    article_type = models.CharField(max_length=10, choices=(('0', '草稿'), ('1', '软删除'), ('2', '正常')), default='2',
                                    verbose_name='文章类别')
    article_original = models.CharField(max_length=10, choices=(('1', '原创'), ('0', '转载')), default='1',
                                        verbose_name='是否原创')
    article_click = models.PositiveIntegerField(verbose_name='文章点击量', default=0)
    article_up = models.CharField(max_length=10, choices=(('1', '置顶'), ('0', '取消置顶')), default='1',
                                  verbose_name='文章置顶')
    article_support = models.CharField(max_length=10, choices=(("1", '推荐'), ('0', '取消推荐')), default='1',
                                       verbose_name="文章推荐")
    article_like = models.IntegerField(verbose_name='顶', default=0)
    article_down = models.IntegerField(verbose_name='踩', default=0)
    article_create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
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


