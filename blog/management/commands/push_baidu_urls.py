# coding=utf-8
from __future__ import unicode_literals

from datetime import timedelta

import requests
from django.core.management.base import BaseCommand
from django.utils import timezone

from MyBlog.env import env
from blog.models import Article
from blog.seo import TOOL_PAGES, absolute_url, site_base_url


class Command(BaseCommand):
    help = 'Push recent public URLs to Baidu active URL submit API.'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=3)
        parser.add_argument('--limit', type=int, default=50)
        parser.add_argument('--dry-run', action='store_true', default=False)

    def build_urls(self, days, limit):
        urls = [
            absolute_url('/'),
            absolute_url('/radar/'),
            absolute_url('/tools/'),
            absolute_url('/sponsor/'),
        ]
        for tool in TOOL_PAGES:
            urls.append(absolute_url('/tools/%s/' % tool['slug']))

        cutoff = timezone.now() - timedelta(days=max(days, 1))
        articles = Article.objects.filter(
            article_type='2',
            article_update_time__gte=cutoff,
        ).order_by('-article_update_time')[:max(limit, 1)]
        for article in articles:
            urls.append(absolute_url('/blog/%s' % article.id))
        return list(dict.fromkeys(urls))

    def handle(self, *args, **options):
        token = env('BAIDU_PUSH_TOKEN', '')
        urls = self.build_urls(options['days'], options['limit'])
        if options['dry_run']:
            for url in urls:
                self.stdout.write(url)
            self.stdout.write(self.style.SUCCESS('dry-run %s url(s)' % len(urls)))
            return
        if not token:
            self.stdout.write(self.style.WARNING('BAIDU_PUSH_TOKEN is empty, skip push.'))
            return

        endpoint = 'http://data.zz.baidu.com/urls?site=%s&token=%s' % (site_base_url(), token)
        response = requests.post(
            endpoint,
            data='\n'.join(urls).encode('utf-8'),
            headers={'Content-Type': 'text/plain'},
            timeout=10,
        )
        self.stdout.write(response.text)
        if response.status_code >= 400:
            self.stdout.write(self.style.WARNING('baidu push skipped or failed, status=%s' % response.status_code))
            return
        self.stdout.write(self.style.SUCCESS('pushed %s url(s)' % len(urls)))
