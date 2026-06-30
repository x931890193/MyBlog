# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0019_sponsorad'),
    ]

    operations = [
        migrations.AddField(
            model_name='sponsorad',
            name='image_url',
            field=models.URLField(blank=True, default='', max_length=500, verbose_name='广告图片'),
        ),
        migrations.AlterField(
            model_name='sponsorad',
            name='placement',
            field=models.CharField(choices=[('sidebar', '侧栏商业位'), ('article_bottom', '文章底部'), ('tools', '工具页'), ('radar', '技术雷达'), ('sponsor', '赞助页')], db_index=True, default='sidebar', max_length=32, verbose_name='展示位置'),
        ),
    ]
