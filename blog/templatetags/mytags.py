# coding=utf-8

# 导入基本配置文件
from django import template
from django.utils.safestring import mark_safe
from markdown import markdown

from ..models import Article

register = template.Library()


# 自定义过滤器

@register.filter(name='toMarkdown')
def toMarkdown(str):
    """markdown解析器"""
    return mark_safe(markdown(str))


@register.filter(name='cat_count')
def cat_count(cat_id):
    """统计分类下边的日志数"""
    return Article.objects.filter(article_category=cat_id).count()
