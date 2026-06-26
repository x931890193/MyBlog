# encoding: utf-8
"""
Create on: 2018-08-12 下午11:23
author: sato
mail: ysudqfs@163.com
life is short, you need python
"""

from django.db import DatabaseError
from redis.exceptions import RedisError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_excepion_handler

from MyBlog.settings import logger


def exception_handler(exc, context):
    """
    捕捉自定义异常
    :param exc: 异常
    :param context: 跑出异常的上下文
    :return: Response 响应对象
    """
    # 调用原生REST的异常处理方法
    response = drf_excepion_handler(exc, context)
    if response is None:
        view = context["view"]
        if isinstance(exc, DatabaseError) or isinstance(exc, RedisError):
            # 数据库异常
            logger.error("[{}] {}".format(view, exc))
            response = Response({"message": "服务器数据库异常！"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return response
