# coding=utf-8
from __future__ import unicode_literals

import re

from django.utils.html import strip_tags

from MyBlog.env import env


SITE_BASE_URL_DEFAULT = 'https://www.mongona.com'

TOOL_PAGES = [
    {
        'name': 'JSON 格式化',
        'slug': 'json-format',
        'desc': '在线格式化、压缩和检查 JSON，适合接口调试、日志排查和配置整理。',
        'detail': '输入内容只在浏览器本地处理，适合排查接口返回、配置文件和日志片段。',
        'use_cases': ['接口联调', '日志排查', '配置整理'],
    },
    {
        'name': 'JWT 解析',
        'slug': 'jwt-decode',
        'desc': '本地解析 JWT Header 和 Payload，快速检查 Token 内容。',
        'detail': '不用上传 Token，就能快速查看 Header、Payload、过期时间和自定义字段。',
        'use_cases': ['登录排障', '权限字段核对', 'Token 调试'],
    },
    {
        'name': '时间戳转换',
        'slug': 'timestamp-converter',
        'desc': '秒、毫秒时间戳和本地时间互转，适合排查日志和接口时间字段。',
        'detail': '支持秒级和毫秒级时间戳，方便对齐接口、日志、数据库里的时间字段。',
        'use_cases': ['日志定位', '接口时间校验', '数据回溯'],
    },
    {
        'name': 'Cron 表达式速查',
        'slug': 'cron-expression',
        'desc': '解释 5 段 Cron 表达式，快速确认定时任务执行周期。',
        'detail': '面向 Linux crontab 的 5 段表达式，适合检查采集、备份、推送等定时任务。',
        'use_cases': ['定时任务检查', '采集计划', '运维排障'],
    },
    {
        'name': 'SQL 格式化',
        'slug': 'sql-format',
        'desc': '在线整理 SQL 缩进和关键字换行，适合排查慢 SQL、接口日志和数据库脚本。',
        'detail': '在浏览器本地做轻量格式化，方便阅读 SELECT、JOIN、WHERE、ORDER BY 等常见语句。',
        'use_cases': ['慢 SQL 排查', '日志阅读', '脚本整理'],
    },
    {
        'name': 'Markdown 预览',
        'slug': 'markdown-preview',
        'desc': '本地预览 Markdown 常用语法并生成安全 HTML 片段，适合写文档和技术笔记。',
        'detail': '支持标题、加粗、行内代码和段落换行，输入内容不上传服务器。',
        'use_cases': ['技术文档', '文章草稿', 'README 编写'],
    },
    {
        'name': '颜色转换器',
        'slug': 'color-converter',
        'desc': 'HEX、RGB、HSL 颜色值互转，适合前端样式调试和 UI 配色核对。',
        'detail': '输入 #0071e3 或 rgb(0,113,227)，快速得到 RGB、HEX 和 HSL 表达。',
        'use_cases': ['CSS 调试', 'UI 配色', '设计还原'],
    },
    {
        'name': 'HTTP 状态码速查',
        'slug': 'http-status',
        'desc': '快速查询常见 HTTP 状态码含义，适合接口联调、Nginx 排障和日志分析。',
        'detail': '覆盖 2xx、3xx、4xx、5xx 常用状态码，帮助快速判断接口问题方向。',
        'use_cases': ['接口联调', '网关排障', '日志分析'],
    },
    {
        'name': 'CIDR 计算器',
        'slug': 'cidr-calculator',
        'desc': 'IPv4 CIDR 网段计算，输出网络地址、广播地址、子网掩码和可用地址范围。',
        'detail': '适合云服务器安全组、Nginx 白名单、Redis/MySQL 访问控制等场景。',
        'use_cases': ['内网规划', '安全组配置', '白名单排查'],
    },
    {
        'name': 'Dockerfile 生成器',
        'slug': 'dockerfile-generator',
        'desc': '按 Python、Node、Go、Nginx 场景生成基础 Dockerfile 片段。',
        'detail': '输出可直接作为项目容器化起点，适合快速搭建开发、部署和演示环境。',
        'use_cases': ['容器化起步', '部署模板', '项目脚手架'],
    },
    {
        'name': 'URL 编码解码',
        'slug': 'url-codec',
        'desc': '在线进行 URL encode/decode，适合处理查询参数、回调地址和日志中的链接。',
        'detail': '输入内容只在浏览器本地处理，便于快速定位参数转义、中文路径和特殊字符问题。',
        'use_cases': ['查询参数排查', '回调地址调试', '中文路径处理'],
    },
    {
        'name': 'Base64 编码解码',
        'slug': 'base64-codec',
        'desc': 'Base64 编码、解码和 UTF-8 文本转换，适合调试配置、Token 片段和接口字段。',
        'detail': '支持中文文本，输出仅在当前浏览器内生成，不上传输入内容。',
        'use_cases': ['配置调试', '接口字段检查', '文本转换'],
    },
    {
        'name': 'SHA 哈希生成器',
        'slug': 'hash-generator',
        'desc': '生成 SHA-1、SHA-256、SHA-384 和 SHA-512 哈希，用于校验文本和排查签名字段。',
        'detail': '基于浏览器 Web Crypto API 计算，适合快速生成摘要和比对签名输入。',
        'use_cases': ['签名排查', '摘要校验', 'Webhook 调试'],
    },
    {
        'name': 'UUID 生成器',
        'slug': 'uuid-generator',
        'desc': '一键生成 UUID v4，适合测试数据、请求 ID、Trace ID 和临时主键。',
        'detail': '优先使用浏览器原生随机 UUID，兼容环境会自动降级生成。',
        'use_cases': ['测试数据', 'Trace ID', '临时主键'],
    },
    {
        'name': '正则表达式测试',
        'slug': 'regex-tester',
        'desc': '在线测试 JavaScript 正则表达式，查看匹配结果和捕获分组。',
        'detail': '适合快速验证日志解析、表单校验和文本提取规则。',
        'use_cases': ['日志解析', '表单校验', '文本提取'],
    },
    {
        'name': 'User-Agent 解析',
        'slug': 'user-agent-parser',
        'desc': '快速解析 User-Agent 中的浏览器、操作系统和设备类型。',
        'detail': '用于排查兼容性问题、移动端访问识别和日志分析。',
        'use_cases': ['访问日志分析', '兼容性排查', '移动端识别'],
    },
]


STATIC_SITEMAP_PAGES = [
    {'path': '/', 'changefreq': 'daily', 'priority': '1.0'},
    {'path': '/rss.xml', 'changefreq': 'daily', 'priority': '0.6'},
    {'path': '/feed.xml', 'changefreq': 'daily', 'priority': '0.6'},
    {'path': '/radar/', 'changefreq': 'daily', 'priority': '0.9'},
    {'path': '/tools/', 'changefreq': 'weekly', 'priority': '0.9'},
    {'path': '/sponsor/', 'changefreq': 'weekly', 'priority': '0.7'},
    {'path': '/?c=4', 'changefreq': 'weekly', 'priority': '0.6'},
    {'path': '/?c=6', 'changefreq': 'monthly', 'priority': '0.5'},
]


def site_base_url():
    return (env('SITE_BASE_URL', SITE_BASE_URL_DEFAULT) or SITE_BASE_URL_DEFAULT).rstrip('/')


def absolute_url(path):
    if not path:
        path = '/'
    if path.startswith(('http://', 'https://')):
        return path
    if not path.startswith('/'):
        path = '/' + path
    return site_base_url() + path


def meta_description(value, fallback='', max_length=155):
    text = strip_tags(value or fallback or '')
    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) > max_length:
        return text[:max_length - 1].rstrip() + '…'
    return text


def tool_by_slug(slug):
    for tool in TOOL_PAGES:
        if tool['slug'] == slug:
            return tool
    return None
