# coding=utf-8
from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from spider.tech_news import import_tech_news


class Command(BaseCommand):
    help = 'Import technology news from public RSS/Atom feeds as attributed repost summaries.'

    def add_arguments(self, parser):
        parser.add_argument('--max-items', type=int, default=12)
        parser.add_argument('--per-source', type=int, default=3)
        parser.add_argument('--author-id', type=int, default=None)
        parser.add_argument('--category-id', type=int, default=None)
        parser.add_argument('--dry-run', action='store_true', default=False)
        parser.add_argument('--update-existing', action='store_true', default=False)

    def handle(self, *args, **options):
        created, results = import_tech_news(
            max_items=options['max_items'],
            per_source=options['per_source'],
            author_id=options.get('author_id'),
            category_id=options.get('category_id'),
            dry_run=options['dry_run'],
            update_existing=options['update_existing'],
        )
        for item in results:
            title = item.get('title') or item.get('message') or ''
            category = item.get('category')
            category_label = ' [{category}]'.format(category=category) if category else ''
            self.stdout.write('[{source}] {status}{category_label} {title}'.format(
                source=item['source'],
                status=item['status'],
                category_label=category_label,
                title=title,
            ))
        label = 'would import' if options['dry_run'] else 'imported'
        self.stdout.write(self.style.SUCCESS('{label} {count} item(s)'.format(label=label, count=created)))
