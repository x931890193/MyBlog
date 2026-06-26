# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0017_article_utf8mb4_and_lengths'),
    ]

    operations = [
        migrations.CreateModel(
            name='SponsorLead',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80, verbose_name='姓名/称呼')),
                ('company', models.CharField(blank=True, default='', max_length=120, verbose_name='公司/产品')),
                ('contact', models.CharField(max_length=160, verbose_name='联系方式')),
                ('demand_type', models.CharField(choices=[('sponsor', '赞助投放'), ('custom_tool', '工具定制'), ('consult', '技术咨询'), ('content', '内容合作'), ('automation', '采集与自动化'), ('other', '其他需求')], default='sponsor', max_length=32, verbose_name='需求类型')),
                ('budget', models.CharField(choices=[('unknown', '暂未确定'), ('lt_1k', '1000 元以内'), ('1k_5k', '1000-5000 元'), ('5k_20k', '5000-20000 元'), ('gt_20k', '20000 元以上')], default='unknown', max_length=32, verbose_name='预算')),
                ('message', models.TextField(blank=True, default='', verbose_name='需求描述')),
                ('source_path', models.CharField(blank=True, default='', max_length=512, verbose_name='提交来源')),
                ('referer', models.CharField(blank=True, default='', max_length=1024, verbose_name='来路')),
                ('user_agent', models.CharField(blank=True, default='', max_length=512, verbose_name='User Agent')),
                ('ip', models.GenericIPAddressField(blank=True, null=True, verbose_name='访问 IP')),
                ('status', models.CharField(choices=[('new', '新线索'), ('contacted', '已联系'), ('qualified', '有效机会'), ('won', '已成交'), ('lost', '已关闭')], db_index=True, default='new', max_length=20, verbose_name='跟进状态')),
                ('note', models.TextField(blank=True, default='', verbose_name='跟进备注')),
                ('time_create', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='提交时间')),
                ('time_modify', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'ordering': ('-time_create',),
                'verbose_name': '合作线索',
                'verbose_name_plural': '合作线索',
            },
        ),
    ]
