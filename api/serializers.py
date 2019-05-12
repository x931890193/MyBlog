# encoding: utf-8
"""
Create on: 2018-08-13 下午7:28
author: sato
mail: ysudqfs@163.com
life is short, you need python
"""
from api.search_indexes import PoetryIndex
from rest_framework import serializers

from .models import ChinesePoems, ChinesePoetry, PoemsAuthors, PoetryAuthors, AddressInfo, ChineseUniversity


class PoemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChinesePoems
        fields = "__all__"
        depth = 1


class PoemsAuthorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PoemsAuthors
        fields = "__all__"
        depth = 1


class PoetrySerializer(serializers.ModelSerializer):
    class Meta:
        model = ChinesePoetry
        fields = "__all__"
        depth = 1


class PoetryAuthorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PoetryAuthors
        fields = "__all__"
        depth = 1


class AreaSerializer(serializers.ModelSerializer):
    """
    行政区划信息序列化器
    """

    class Meta:
        model = AddressInfo
        fields = ('id', 'name')  # 元组或列表


class SubAreaSerializer(serializers.ModelSerializer):
    """
    子行政区划信息序列化器
    """
    subs = AreaSerializer(many=True, read_only=True)

    class Meta:
        model = AddressInfo
        fields = ('id', 'name', 'subs')


# 搜索
from drf_haystack.serializers import HaystackSerializer


class PoetryIndexSerializer(HaystackSerializer):
    """
    索引结果数据序列化器
    """
    object = PoetrySerializer(read_only=True)

    class Meta:
        index_classes = [PoetryIndex]
        fields = ('text', 'object')


class ChineseUniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ChineseUniversity
        fields = "__all__"
        depth = 1
