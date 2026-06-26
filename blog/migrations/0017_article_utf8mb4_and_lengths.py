# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0016_auto_20200529_2114'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='article_title',
            field=models.CharField(default='', max_length=180, verbose_name='日志标题'),
        ),
        migrations.AlterField(
            model_name='article',
            name='article_tag',
            field=models.CharField(default='', max_length=120, verbose_name='日志标签'),
        ),
        migrations.RunSQL(
            ["ALTER TABLE blog_article CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"],
            ["ALTER TABLE blog_article CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci"],
        ),
    ]
