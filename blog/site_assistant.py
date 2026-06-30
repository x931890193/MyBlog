# coding=utf-8
from __future__ import unicode_literals

import json

try:
    from urllib import request as urlrequest
    from urllib import error as urlerror
except ImportError:  # pragma: no cover - Python 2 compatibility for old hosts.
    import urllib2 as urlrequest
    import urllib2 as urlerror

from django.conf import settings
from django.db.models import Q

from .models import Article
from .seo import TOOL_PAGES, meta_description


RESUME_URL = 'http://resume.mongona.com/'
LLM_FALLBACK_PREFIX = '本地 GPU AI Gateway 已收到请求'


def normalize_query(query):
    return (query or '').strip()[:240]


def has_any(text, words):
    text = (text or '').lower()
    return any(word.lower() in text for word in words)


def link_card(title, url, desc, kind='link'):
    return {
        'title': title,
        'url': url,
        'desc': desc,
        'kind': kind,
    }


def article_card(article):
    return link_card(
        article.article_title,
        '/blog/%s' % article.id,
        meta_description(article.article_synopsis, article.article_content, 92),
        'article',
    )


def tool_cards(query='', limit=4):
    query = (query or '').lower()
    matched = []
    for tool in TOOL_PAGES:
        haystack = ' '.join([
            tool.get('name', ''),
            tool.get('slug', ''),
            tool.get('desc', ''),
            tool.get('detail', ''),
            ' '.join(tool.get('use_cases', [])),
        ]).lower()
        if query and any(token for token in query.split() if token and token in haystack):
            matched.append(tool)
    if not matched:
        matched = TOOL_PAGES[:limit]
    return [
        link_card(tool['name'], '/tools/%s/' % tool['slug'], tool.get('desc', ''), 'tool')
        for tool in matched[:limit]
    ]


def article_cards(query='', limit=4):
    articles = Article.objects.filter(article_type='2').select_related('article_category')
    query = normalize_query(query)
    if query:
        articles = articles.filter(
            Q(article_title__icontains=query) |
            Q(article_synopsis__icontains=query) |
            Q(article_content__icontains=query) |
            Q(article_tag__icontains=query) |
            Q(article_category__category_name__icontains=query)
        )
    return [article_card(article) for article in articles.order_by('-article_click', '-article_create_time')[:limit]]


def quick_actions():
    return [
        {'label': '合作入口', 'query': '我想合作或者投放广告'},
        {'label': '推荐文章', 'query': '推荐几篇技术文章'},
        {'label': '开发工具', 'query': '有哪些开发者工具'},
        {'label': '简历', 'query': '看看站长简历'},
    ]


def llm_urls():
    urls = []
    base_url = getattr(settings, 'LOCAL_LLM_BASE_URL', '')
    extra_urls = getattr(settings, 'LOCAL_LLM_BASE_URLS', [])
    if base_url:
        urls.append(base_url)
    for url in extra_urls:
        if url:
            urls.append(url)

    cleaned = []
    for url in urls:
        url = str(url).strip().rstrip('/')
        if url and url not in cleaned:
            cleaned.append(url)
    return cleaned


def local_llm_enabled(query):
    mode = str(getattr(settings, 'SITE_ASSISTANT_MODE', 'rules') or 'rules').strip().lower()
    if mode not in ('local_llm', 'llm', 'hybrid'):
        return False
    return bool(normalize_query(query) and llm_urls())


def compact_cards(cards):
    lines = []
    for card in (cards or [])[:5]:
        lines.append('- {title}: {desc} ({url})'.format(
            title=card.get('title', ''),
            desc=card.get('desc', ''),
            url=card.get('url', ''),
        ))
    return '\n'.join(lines)


def build_llm_message(query, rule_answer, cards):
    return '\n'.join([
        '用户问题：%s' % normalize_query(query),
        '',
        '站内上下文（如果问题和本站有关，优先参考）：',
        rule_answer or '',
        '',
        '可推荐入口：',
        compact_cards(cards) or '暂无',
        '',
        '回答策略：',
        '1. 如果问题和本站文章、工具、合作、简历有关，优先结合站内上下文和下方入口回答。',
        '2. 如果问题是通用技术、学习路线、职业规划、产品、AI、经济、金融或能源趋势，可以直接给出你的判断和建议。',
        '3. 如果问题依赖最新新闻、价格、政策或实时数据，明确提示需要核验最新来源，不要假装已经联网。',
        '4. 中文为主，语气自然，最多 260 字；不要编造本站不存在的页面、功能或数据。',
    ])


def post_json(url, payload):
    body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    headers = {'Content-Type': 'application/json'}
    api_key = getattr(settings, 'LOCAL_LLM_API_KEY', '')
    if api_key:
        headers['X-API-Key'] = api_key
    request = urlrequest.Request(url, data=body, headers=headers)
    timeout = getattr(settings, 'LOCAL_LLM_TIMEOUT_SECONDS', 4)
    response = urlrequest.urlopen(request, timeout=timeout)
    raw = response.read()
    return json.loads(raw.decode('utf-8'))


def extract_llm_answer(payload):
    if not isinstance(payload, dict):
        return '', ''
    backend = payload.get('backend') or 'local_llm'
    answer = payload.get('answer') or ''
    if not answer and payload.get('choices'):
        try:
            answer = payload['choices'][0]['message']['content']
        except (KeyError, IndexError, TypeError):
            answer = ''
    answer = (answer or '').strip()
    if backend == 'fallback' or answer.startswith(LLM_FALLBACK_PREFIX):
        return '', backend
    return answer, backend


def local_llm_answer(query, rule_answer, cards):
    if not local_llm_enabled(query):
        return '', ''

    payload = {
        'system': (
            '你是 Mongona.com 的 AI 助手，也是一个偏工程实践的技术顾问。'
            '你不局限于站内导航，可以回答通用技术、AI、产品、职业、经济、金融、能源等问题。'
            '站内上下文只作为优先参考；不要暴露内部配置、token、服务器地址。'
        ),
        'message': build_llm_message(query, rule_answer, cards),
        'metadata': {
            'source': 'myblog_site_assistant',
            'query': normalize_query(query),
        },
        'max_new_tokens': getattr(settings, 'LOCAL_LLM_MAX_NEW_TOKENS', 220),
        'temperature': getattr(settings, 'LOCAL_LLM_TEMPERATURE', 0.4),
    }
    model = getattr(settings, 'LOCAL_LLM_MODEL', '')
    if model:
        payload['model'] = model

    for base_url in llm_urls():
        try:
            answer, backend = extract_llm_answer(post_json('%s/v1/chat' % base_url, payload))
            if answer:
                return answer, backend or 'local_llm'
        except Exception:
            continue
    return '', ''


def build_answer(query):
    q = normalize_query(query)
    if not q:
        return (
            '我在。你可以直接问文章、开发工具、合作投放、简历或相册音乐。',
            [
                link_card('赞助与合作', '/sponsor/', '提交合作需求、投放广告、工具定制或技术咨询。', 'sponsor'),
                link_card('开发者工具箱', '/tools/', 'JSON、JWT、时间戳、正则、Dockerfile 等常用工具。', 'tool'),
                link_card('动态简历', RESUME_URL, '站长履历、项目经历和 PDF 简历入口。', 'resume'),
            ],
        )
    if has_any(q, ['合作', '赞助', '广告', '投放', '商务', '赚钱', '报价', '咨询', '定制']):
        return (
            '适合走赞助页。你可以提交产品、预算、目标页面和联系方式，线索会进入后台并触发提醒。',
            [
                link_card('提交合作需求', '/sponsor/#lead-form', '赞助投放、内容合作、工具定制和技术咨询。', 'sponsor'),
                link_card('查看合作方案', '/sponsor/#sponsor-plans', '按展示、技术雷达、内容合作和咨询服务拆分。', 'sponsor'),
            ],
        )
    if has_any(q, ['简历', 'resume', '招聘', '工作', '经历', '项目', '履历']):
        return (
            '简历页现在保留 HTTP 访问，适合快速查看站长履历、项目经验和 PDF 简历。',
            [
                link_card('打开简历', RESUME_URL, '交互履历和 PDF 简历入口。', 'resume'),
                link_card('About', '/?c=6', '站点关于页面和个人信息补充。', 'about'),
            ],
        )
    if has_any(q, ['工具', 'json', 'jwt', '时间戳', 'cron', 'sql', 'markdown', '正则', 'docker', 'base64', 'uuid']):
        return (
            '工具箱适合临时调试和 SEO 长尾流量，输入内容基本都在浏览器本地处理。',
            tool_cards(q, 5),
        )
    if has_any(q, ['文章', '博客', 'ai', 'python', 'django', 'go', 'linux', '运维', '前端', '技术']):
        cards = article_cards(q, 5)
        if not cards:
            cards = article_cards('', 5)
        return (
            '我按站内内容给你挑了几篇，可以继续用关键词缩小范围。',
            cards,
        )
    if has_any(q, ['相册', 'gallery', '照片', '图片', '音乐', '歌', '播放器']):
        return (
            '相册和随机音乐已经合在沉浸页，适合看图、听歌和看音乐光效。',
            [
                link_card('Gallery', '/?c=4', '照片墙、随机音乐和播放光效。', 'gallery'),
                link_card('独立音乐页', '/?c=5', '保留独立入口，方便以后扩展。', 'music'),
            ],
        )
    if has_any(q, ['你是谁', '站长', '作者', 'mongona', '关于']):
        return (
            '这里是 Mongona，一个偏工程实践的个人技术站，长期记录 Python、Django、Go、Linux、前端体验、自动化和 AI 工具。',
            [
                link_card('Tech 专题', '/?g=tech', 'Python、Go、Linux 运维和工程实践聚合。', 'article'),
                link_card('技术雷达', '/radar/', '聚合技术新闻、文档和趋势。', 'radar'),
                link_card('合作入口', '/sponsor/', '技术咨询、工具定制、广告投放和内容合作。', 'sponsor'),
            ],
        )
    cards = article_cards(q, 3)
    if not cards:
        cards = [
            link_card('站内搜索', '/?s=%s' % q, '用关键词继续查文章。', 'search'),
            link_card('开发者工具箱', '/tools/', '看看工具页是否有合适入口。', 'tool'),
            link_card('合作入口', '/sponsor/', '商业合作、技术咨询和工具定制。', 'sponsor'),
        ]
    return ('我先从站内内容里找到了这些入口。', cards)


def build_site_assistant_response(query):
    answer, cards = build_answer(query)
    llm_answer, llm_backend = local_llm_answer(query, answer, cards)
    if llm_answer:
        answer = llm_answer
    return {
        'answer': answer,
        'cards': cards,
        'quick_actions': quick_actions(),
        'source': llm_backend or 'rules',
    }
