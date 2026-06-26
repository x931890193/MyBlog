# coding=utf-8
from __future__ import unicode_literals

import hashlib
import re
from datetime import datetime
from email.utils import parsedate_to_datetime
from html import escape, unescape
from xml.etree import ElementTree

import requests
from django.conf import settings
from django.db import IntegrityError
from django.utils import timezone

from blog.models import Article, Category, UserProfile


TECH_NEWS_FEEDS = [
    {
        'name': 'InfoQ China',
        'url': 'https://www.infoq.cn/feed',
        'tag': '中文技术 RSS',
        'category': 'Operation',
    },
    {
        'name': '阮一峰的网络日志',
        'url': 'https://www.ruanyifeng.com/blog/atom.xml',
        'tag': '中文技术 RSS',
        'category': 'Operation',
    },
    {
        'name': '美团技术团队',
        'url': 'https://tech.meituan.com/feed/',
        'tag': '中文技术 RSS',
        'category': 'Operation',
    },
    {
        'name': 'OSCHINA News',
        'url': 'https://www.oschina.net/news/rss',
        'tag': '开源 新闻 RSS',
        'category': 'Open Source',
    },
    {
        'name': 'OSCHINA Industry',
        'url': 'https://www.oschina.net/news/rss?show=industry',
        'tag': '开源 行业 RSS',
        'category': 'Open Source',
    },
    {
        'name': '少数派',
        'url': 'https://sspai.com/feed',
        'tag': '效率 数字生活 RSS',
        'category': 'Operation',
    },
    {
        'name': '量子位',
        'url': 'https://www.qbitai.com/feed',
        'tag': 'AI 中文 RSS',
        'category': 'AI',
    },
    {
        'name': '雷峰网',
        'url': 'https://www.leiphone.com/feed',
        'tag': 'AI 科技 RSS',
        'category': 'AI',
    },
    {
        'name': 'Python Insider',
        'url': 'https://blog.python.org/feeds/posts/default?alt=rss',
        'tag': 'Python RSS',
        'category': 'Python',
    },
    {
        'name': 'Django Weblog',
        'url': 'https://www.djangoproject.com/rss/weblog/',
        'tag': 'Django RSS',
        'category': 'Python',
    },
    {
        'name': 'Mozilla Hacks',
        'url': 'https://hacks.mozilla.org/feed/',
        'tag': 'Web RSS',
        'category': 'Web',
    },
    {
        'name': 'GitHub Blog',
        'url': 'https://github.blog/feed/',
        'tag': 'GitHub RSS',
        'category': 'Open Source',
    },
    {
        'name': 'Kubernetes Blog',
        'url': 'https://kubernetes.io/feed.xml',
        'tag': 'Kubernetes RSS',
        'category': 'Docker',
    },
    {
        'name': 'Cloudflare Blog',
        'url': 'https://blog.cloudflare.com/rss/',
        'tag': 'Infra RSS',
        'category': 'Operation',
    },
    {
        'name': 'DEV Community',
        'url': 'https://dev.to/feed',
        'tag': 'Forum RSS',
        'category': 'Operation',
    },
    {
        'name': 'OpenAI News',
        'url': 'https://openai.com/news/rss.xml',
        'tag': 'AI RSS',
        'category': 'AI',
    },
]

HEADERS = {
    'User-Agent': 'mongona-tech-news-bot/1.0 (+https://www.mongona.com/)',
    'Accept': 'application/rss+xml, application/atom+xml, application/xml, text/xml;q=0.9, */*;q=0.8',
}

CATEGORY_RULES = [
    (('AI', 'ai', 'aigc', 'openai', '人工智能', '大模型'), [
        'ai', 'aigc', 'openai', 'chatgpt', 'gpt', 'claude', 'llm', 'agent', 'agents',
        'nvidia', 'neural', 'machine learning', 'deep learning', '大模型', '人工智能',
        '智能体', '模型', '机器人',
    ]),
    (('安全', 'security'), [
        'security', 'secure', 'securing', 'cve', 'cwe', 'vulnerability', 'exploit',
        'prompt injection', 'harden', 'hardening', '安全', '漏洞', '攻防',
    ]),
    (('开源', 'open source', 'opensource', 'github', 'oschina'), [
        'open source', 'opensource', 'github', 'maintainer', 'repository', 'repo',
        '开源', '社区', '贡献者',
    ]),
    (('Web', 'web', 'frontend', '前端'), [
        'web', 'frontend', 'javascript', 'typescript', 'css', 'html', 'browser',
        'firefox', 'mozilla', 'react', 'vue', '前端', '浏览器',
    ]),
    (('docker', '容器'), [
        'docker', 'kubernetes', 'k8s', 'container',
    ]),
    (('数据库', 'database'), [
        'mysql', 'postgres', 'postgresql', 'redis', 'mongodb', 'database', 'sql server', '数据库',
    ]),
    (('rust',), [
        'rust', 'cargo',
    ]),
    (('lua',), [
        'lua', 'openresty',
    ]),
    (('go语言', 'golang'), [
        'golang', 'go 语言', 'go语言',
    ]),
    (('python', 'python编程'), [
        'python', 'django', 'flask', 'fastapi', 'pandas', 'numpy', 'pytorch', 'bert',
    ]),
    (('liunx', 'linux', 'operation', '运维'), [
        'linux', 'liunx', 'devops', 'sre', 'cloudflare', 'infra', 'infrastructure',
        'android', 'harmonyos', '鸿蒙', '云', '部署', '运维',
    ]),
]

CATEGORY_DEFAULTS = {
    'AI': {
        'name': 'AI',
        'detail': 'AI、大模型、智能体与机器学习资讯',
        'icon': 'am-icon-magic',
        'sort': 11,
        'aliases': ('AI', 'ai', 'aigc', 'openai', '人工智能', '大模型'),
    },
    'Web': {
        'name': 'Web',
        'detail': 'Web、前端、浏览器与 JavaScript 生态',
        'icon': 'am-icon-html5',
        'sort': 12,
        'aliases': ('Web', 'web', 'frontend', '前端'),
    },
    'Open Source': {
        'name': '开源',
        'detail': '开源社区、GitHub 与工程生态',
        'icon': 'am-icon-code-fork',
        'sort': 13,
        'aliases': ('开源', 'open source', 'opensource', 'github', 'oschina'),
    },
    'Security': {
        'name': '安全',
        'detail': '安全、漏洞、攻防与软件供应链风险',
        'icon': 'am-icon-shield',
        'sort': 14,
        'aliases': ('安全', 'security', 'cve', 'cwe'),
    },
}

CATEGORY_HINTS = {
    'Python': ('python', 'python编程'),
    'Docker': ('docker', '容器'),
    'Operation': ('liunx', 'linux', 'operation', '运维'),
    'AI': CATEGORY_DEFAULTS['AI']['aliases'],
    'Web': CATEGORY_DEFAULTS['Web']['aliases'],
    'Open Source': CATEGORY_DEFAULTS['Open Source']['aliases'],
    'Security': CATEGORY_DEFAULTS['Security']['aliases'],
}

SOURCE_HINT_FIRST = ('Python', 'Docker', 'Web')


def local_name(tag):
    return tag.rsplit('}', 1)[-1].lower()


def child_text(node, names):
    names = set(names)
    for child in list(node):
        if local_name(child.tag) in names:
            return ''.join(child.itertext()).strip()
    return ''


def entry_link(node):
    link = child_text(node, ['link'])
    if link:
        return link
    for child in list(node):
        if local_name(child.tag) == 'link':
            rel = child.attrib.get('rel', 'alternate')
            href = child.attrib.get('href')
            if href and rel == 'alternate':
                return href
    return ''


def clean_text(value, limit=500):
    value = re.sub(r'(?is)<(script|style).*?>.*?</\1>', ' ', value or '')
    value = re.sub(r'(?s)<[^>]+>', ' ', value)
    value = unescape(value)
    value = re.sub(r'\s+', ' ', value).strip()
    if len(value) > limit:
        return value[:limit].rstrip() + '...'
    return value


def parse_datetime(value):
    if not value:
        return None
    try:
        dt = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        try:
            dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except (TypeError, ValueError):
            return None
    if getattr(settings, 'USE_TZ', False):
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt, timezone.get_current_timezone())
    elif timezone.is_aware(dt):
        dt = timezone.make_naive(dt, timezone.get_current_timezone())
    return dt


def truncate(value, limit):
    value = value or ''
    if len(value) <= limit:
        return value
    return value[:limit - 3].rstrip() + '...'


def excerpt_html(value):
    text = clean_text(value, 6000)
    if not text:
        return '<p>原文未提供可聚合正文摘录，请点击原文链接阅读。</p>'
    paragraphs = []
    while text:
        paragraphs.append(text[:520].strip())
        text = text[520:].strip()
    return ''.join('<p>{}</p>'.format(escape(item)) for item in paragraphs if item)


def fetch_feed(source, timeout=12):
    response = requests.get(source['url'], headers=HEADERS, timeout=timeout)
    response.raise_for_status()
    return response.content


def parse_feed(content, source, per_source=3):
    root = ElementTree.fromstring(content)
    entries = []
    for node in root.iter():
        if local_name(node.tag) not in ('item', 'entry'):
            continue
        title = clean_text(child_text(node, ['title']), 160)
        link = entry_link(node)
        if not title or not link:
            continue
        summary = child_text(node, ['description', 'summary', 'encoded', 'content'])
        published = child_text(node, ['pubdate', 'published', 'updated', 'date'])
        entries.append({
            'source_name': source['name'],
            'source_url': source['url'],
            'title': title,
            'link': link.strip(),
            'summary': clean_text(summary, 420),
            'excerpt': clean_text(summary, 6000),
            'published_at': parse_datetime(published),
            'tag': source.get('tag', 'Tech RSS'),
            'category': source.get('category', ''),
        })
        if len(entries) >= per_source:
            break
    return entries


def default_author(author_id=None):
    if author_id:
        user = UserProfile.objects.filter(pk=author_id).first()
        if user:
            return user
    return UserProfile.objects.filter(is_superuser=True).first() or UserProfile.objects.first()


def default_category(category_id=None, category_name=''):
    if category_id:
        category = Category.objects.filter(pk=category_id).first()
        if category:
            return category
    categories = list(Category.objects.all())
    category = match_category(categories, (category_name,))
    if category:
        return category
    category = match_category(categories, CATEGORY_HINTS.get('Operation', ()))
    return category or Category.objects.first()


def category_default_for_aliases(aliases):
    alias_set = set(alias.lower() for alias in aliases if alias)
    for item in CATEGORY_DEFAULTS.values():
        default_aliases = set(alias.lower() for alias in item.get('aliases', ()))
        default_aliases.add(item['name'].lower())
        if alias_set & default_aliases:
            return item
    return None


def match_category(categories, aliases, create=False):
    aliases = [alias.lower() for alias in aliases if alias]
    for category in categories:
        name = category.category_name.lower()
        if any(alias == name or alias in name for alias in aliases):
            return category
    if create:
        defaults = category_default_for_aliases(aliases)
        if defaults:
            category, _ = Category.objects.get_or_create(
                category_name=defaults['name'],
                defaults={
                    'category_detail': defaults['detail'],
                    'category_icon': defaults['icon'],
                    'category_sort_id': defaults['sort'],
                },
            )
            categories.append(category)
            return category
    return None


def keyword_matches(text, keyword):
    keyword = (keyword or '').lower()
    if not keyword:
        return False
    if re.match(r'^[a-z0-9+#.]{1,3}$', keyword):
        pattern = r'(?<![a-z0-9]){}(?![a-z0-9])'.format(re.escape(keyword))
        return re.search(pattern, text) is not None
    return keyword in text


def detect_category(item, categories, create=False):
    text = ' '.join([
        item.get('title') or '',
        item.get('summary') or '',
        item.get('excerpt') or '',
        item.get('source_name') or '',
        item.get('tag') or '',
    ]).lower()

    hint = item.get('category')
    if hint in SOURCE_HINT_FIRST:
        category = match_category(categories, CATEGORY_HINTS.get(hint, (hint,)), create=create)
        if category:
            return category

    for aliases, keywords in CATEGORY_RULES:
        if any(keyword_matches(text, keyword) for keyword in keywords):
            category = match_category(categories, aliases, create=create)
            if category:
                return category

    return match_category(categories, CATEGORY_HINTS.get(hint, (hint,)), create=create)


def article_body(item, uid):
    title = escape(item['title'])
    link = escape(item['link'])
    source_name = escape(item['source_name'])
    source_url = escape(item['source_url'])
    summary = escape(item['summary'] or '原文未提供摘要，请点击原文链接阅读。')
    excerpt = excerpt_html(item.get('excerpt') or item['summary'])
    return (
        '<!-- tech-news-id:{uid} -->'
        '<section class="tech-source-card">'
        '<p><strong>转载声明：</strong>本文为技术资讯聚合，来源于 {source_name}。'
        '本站保存公开 Feed 中提供的摘要/摘录和原文链接，方便读者发现内容，不声称原创。</p>'
        '<blockquote>{summary}</blockquote>'
        '<p><a class="source-readmore" href="{link}" target="_blank" rel="nofollow noopener noreferrer">'
        '阅读原文：{title}</a></p>'
        '</section>'
        '<h3>原文摘录</h3>'
        '<div class="source-excerpt">{excerpt}</div>'
        '<p><small>版权归原作者及原站点所有，如原站点不希望被聚合，请联系本站删除。</small></p>'
        '<p><small>来源 Feed：<a href="{source_url}" target="_blank" rel="nofollow noopener noreferrer">{source_name}</a></small></p>'
    ).format(uid=uid, source_name=source_name, summary=summary, excerpt=excerpt, link=link, title=title,
             source_url=source_url)


def create_article(item, author=None, category=None, dry_run=False, update_existing=False):
    uid = hashlib.sha256(item['link'].encode('utf-8')).hexdigest()
    marker = 'tech-news-id:{}'.format(uid)
    existing = Article.objects.filter(article_content__contains=marker).first()
    if existing:
        if update_existing and not dry_run:
            existing.article_synopsis = item['summary'] or item['title']
            existing.article_content = article_body(item, uid)
            existing.article_original = '0'
            if category:
                existing.article_category = category
            existing.save(update_fields=['article_synopsis', 'article_content', 'article_original', 'article_category'])
            return False, 'updated', item['title']
        return False, 'exists', item['title']
    if dry_run:
        return True, 'dry-run', item['title']

    category = category or default_category(category_name=item.get('category'))
    try:
        article = Article.objects.create(
            article_title=truncate(item['title'], 180),
            article_synopsis=item['summary'] or item['title'],
            article_user=author or default_author(),
            article_category=category,
            article_tag=truncate(item.get('tag') or 'Tech RSS', 120),
            article_content=article_body(item, uid),
            article_type='2',
            article_original='0',
            article_up='0',
            article_support='0',
        )
    except IntegrityError as exc:
        return False, 'error: {}'.format(exc), item['title']
    if item.get('published_at'):
        Article.objects.filter(pk=article.pk).update(article_create_time=item['published_at'])
    return True, 'created', item['title']


def import_tech_news(max_items=12, per_source=3, author_id=None, category_id=None, dry_run=False,
                     update_existing=False):
    author = default_author(author_id)
    fallback_category = default_category(category_id) if category_id else None
    categories = list(Category.objects.all())
    results = []
    created = 0
    for source in TECH_NEWS_FEEDS:
        try:
            entries = parse_feed(fetch_feed(source), source, per_source=per_source)
        except Exception as exc:
            results.append({'source': source['name'], 'status': 'fetch-error', 'message': str(exc)})
            continue
        for item in entries:
            category = fallback_category or detect_category(item, categories, create=not dry_run) or default_category(category_name=item.get('category'))
            ok, status, title = create_article(
                item,
                author=author,
                category=category,
                dry_run=dry_run,
                update_existing=update_existing,
            )
            results.append({
                'source': source['name'],
                'status': status,
                'title': title,
                'category': category.category_name if category else '',
            })
            if ok and status in ('created', 'dry-run'):
                created += 1
            if created >= max_items:
                return created, results
    return created, results
