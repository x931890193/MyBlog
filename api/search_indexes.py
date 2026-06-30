# encoding: utf-8
"""
Create on: 2018-08-14 上午12:01
author: sato
mail: ysudqfs@163.com
life is short, you need python
"""
from haystack import indexes

from .models import ChinesePoetry


class PoetryIndex(indexes.SearchIndex, indexes.Indexable):
    """
    索引数据模型类
    """
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        """返回建立索引的模型类"""
        return ChinesePoetry

    def index_queryset(self, using=None):
        """返回要建立索引的数据查询集"""
        # return self.get_model().objects.filter(is_launched=True)
        return self.get_model().objects.all()

