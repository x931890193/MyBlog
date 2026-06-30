# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0018_sponsorlead'),
    ]

    operations = [
        migrations.CreateModel(
            name='SponsorAd',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120, verbose_name='广告标题')),
                ('sponsor_name', models.CharField(blank=True, default='', max_length=120, verbose_name='赞助方')),
                ('description', models.CharField(blank=True, default='', max_length=240, verbose_name='广告描述')),
                ('target_url', models.URLField(max_length=500, verbose_name='目标链接')),
                ('cta_text', models.CharField(default='了解详情', max_length=40, verbose_name='按钮文案')),
                ('placement', models.CharField(choices=[('sidebar', '侧栏商业位'), ('tools', '工具页'), ('radar', '技术雷达'), ('sponsor', '赞助页')], db_index=True, default='sidebar', max_length=32, verbose_name='展示位置')),
                ('priority', models.IntegerField(db_index=True, default=0, verbose_name='排序权重')),
                ('is_active', models.BooleanField(db_index=True, default=True, verbose_name='启用')),
                ('start_at', models.DateTimeField(blank=True, null=True, verbose_name='开始时间')),
                ('end_at', models.DateTimeField(blank=True, null=True, verbose_name='结束时间')),
                ('click_count', models.PositiveIntegerField(default=0, verbose_name='点击数')),
                ('time_create', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='创建时间')),
                ('time_modify', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'ordering': ('placement', '-priority', '-time_create'),
                'verbose_name': '赞助广告位',
                'verbose_name_plural': '赞助广告位',
            },
        ),
    ]
