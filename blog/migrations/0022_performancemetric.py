# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0021_sponsorad_metrics'),
    ]

    operations = [
        migrations.CreateModel(
            name='PerformanceMetric',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('method', models.CharField(db_index=True, default='GET', max_length=8, verbose_name='请求方法')),
                ('path', models.CharField(default='', max_length=512, verbose_name='请求路径')),
                ('path_hash', models.CharField(db_index=True, default='', max_length=32, verbose_name='路径指纹')),
                ('status_code', models.PositiveIntegerField(db_index=True, default=200, verbose_name='状态码')),
                ('duration_ms', models.PositiveIntegerField(db_index=True, default=0, verbose_name='响应耗时(ms)')),
                ('db_query_count', models.PositiveIntegerField(default=0, verbose_name='DB 查询数')),
                ('cache_status', models.CharField(db_index=True, default='skip', max_length=16, verbose_name='页面缓存')),
                ('is_slow', models.BooleanField(db_index=True, default=False, verbose_name='慢请求')),
                ('ip', models.GenericIPAddressField(blank=True, null=True, verbose_name='访问 IP')),
                ('referer', models.CharField(blank=True, default='', max_length=1024, verbose_name='来路')),
                ('user_agent', models.CharField(blank=True, default='', max_length=512, verbose_name='User Agent')),
                ('time_create', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='记录时间')),
            ],
            options={
                'ordering': ('-time_create',),
                'verbose_name': '性能监控',
                'verbose_name_plural': '性能监控',
            },
        ),
    ]
