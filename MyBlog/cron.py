# coding=utf-8
from __future__ import unicode_literals

from django.core.management import call_command


def import_tech_news_daily():
    call_command(
        'import_tech_news',
        max_items=24,
        per_source=2,
        update_existing=True,
    )


def push_baidu_urls_daily():
    call_command(
        'push_baidu_urls',
        days=3,
        limit=80,
    )
