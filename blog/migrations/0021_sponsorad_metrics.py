# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0020_sponsorad_article_bottom_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='sponsorad',
            name='dismiss_count',
            field=models.PositiveIntegerField(default=0, verbose_name='关闭数'),
        ),
        migrations.AddField(
            model_name='sponsorad',
            name='impression_count',
            field=models.PositiveIntegerField(default=0, verbose_name='曝光数'),
        ),
    ]
