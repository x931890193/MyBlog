import hashlib
import ipaddress
import json
import time

import requests
from django.db import connections
from django.http import HttpResponse, HttpResponsePermanentRedirect

from MyBlog.env import env
from MyBlog.utils import redis_client
from blog.models import PerformanceMetric, RequestInfo


PAGE_CACHE_EXCLUDED_PREFIXES = (
    '/api/',
    '/blog/',
    '/ckeditor/',
    '/debug/',
    '/digg/',
    '/duanzi/',
    '/media/',
)


def split_csv(value):
    return [item.strip().lower() for item in _text(value).split(',') if item.strip()]


def request_host(request):
    host = request.get_host().split(':', 1)[0]
    return host.strip().lower()


class CanonicalHostRedirectMiddleware(object):
    def __init__(self, get_response=None):
        self.get_response = get_response
        super().__init__()

    def __call__(self, request):
        if env_bool('CANONICAL_REDIRECT_ENABLED', True):
            canonical_host = _text(env('CANONICAL_HOST', 'www.mongona.com')).strip().lower()
            redirect_hosts = split_csv(env('CANONICAL_REDIRECT_HOSTS', 'mongona.com'))
            host = request_host(request)
            if canonical_host and host in redirect_hosts and host != canonical_host:
                return HttpResponsePermanentRedirect('https://%s%s' % (canonical_host, request.get_full_path()))
        return self.get_response(request)

PERFORMANCE_EXCLUDED_PREFIXES = (
    '/debug/',
    '/media/',
    '/static/',
    '/ckeditor/',
)


def env_int(name, default):
    try:
        return int(env(name, default))
    except (TypeError, ValueError):
        return default


def env_float(name, default):
    try:
        return float(env(name, default))
    except (TypeError, ValueError):
        return default


def env_bool(name, default=False):
    value = env(name)
    if value is None:
        return default
    return str(value).strip().lower() in ('1', 'true', 'yes', 'on')


def clamp_percent(value, default=0):
    return max(0, min(100, env_int(value, default)))


def _text(value):
    if isinstance(value, bytes):
        return value.decode(errors='ignore')
    if value is None:
        return ''
    return str(value)


def short_text(value, max_length):
    value = _text(value)
    return value[:max_length] if len(value) > max_length else value


def _normalize_ip(value):
    value = _text(value).strip()
    if not value or value.lower() == 'unknown':
        return ''
    if value.startswith('[') and ']' in value:
        return value[1:value.index(']')]
    if value.count(':') == 1:
        host, port = value.rsplit(':', 1)
        if port.isdigit():
            return host.strip()
    return value


def get_client_ip(request):
    public_ips = []
    fallback_ips = []
    local_ips = []

    for header in ('HTTP_X_FORWARDED_FOR', 'HTTP_X_REAL_IP', 'REMOTE_ADDR'):
        raw_value = request.META.get(header, '')
        for item in _text(raw_value).split(','):
            ip = _normalize_ip(item)
            if not ip:
                continue
            try:
                parsed = ipaddress.ip_address(ip)
            except ValueError:
                continue

            if parsed.is_loopback or parsed.is_unspecified:
                local_ips.append(ip)
            elif parsed.is_global:
                public_ips.append(ip)
            else:
                fallback_ips.append(ip)

    if public_ips:
        return public_ips[0]
    if fallback_ips:
        return fallback_ips[0]
    if local_ips:
        return local_ips[0]
    return ''


def cache_key(prefix, *parts):
    raw = '|'.join(_text(part) for part in parts)
    return '{}:{}'.format(prefix, hashlib.md5(raw.encode('utf-8')).hexdigest())


def page_cache_seconds():
    return env_int('PAGE_CACHE_SECONDS', 900)


def request_path_with_query(request):
    path = request.META.get('PATH_INFO', '/') or '/'
    query = request.META.get('QUERY_STRING', '')
    if query:
        path += '?' + query
    return path


def query_count_snapshot():
    try:
        return sum(len(connection.queries) for connection in connections.all())
    except Exception:
        return 0


def should_skip_performance_path(path):
    return any(path.startswith(prefix) for prefix in PERFORMANCE_EXCLUDED_PREFIXES)


def should_write_performance_metric(path, path_hash, status_code, is_slow):
    if not env_bool('PERFORMANCE_MONITOR_ENABLED', True):
        return False
    if should_skip_performance_path(path):
        return False
    if status_code >= 500 or is_slow:
        should_sample = True
    else:
        sample_percent = clamp_percent('PERFORMANCE_MONITOR_SAMPLE_PERCENT', 10)
        if sample_percent <= 0:
            return False
        bucket = int(hashlib.md5((path_hash + str(int(time.time() / 60))).encode('utf-8')).hexdigest()[:6], 16)
        should_sample = bucket % 100 < sample_percent
    if not should_sample:
        return False

    interval = env_int('PERFORMANCE_MONITOR_WRITE_INTERVAL_SECONDS', 10)
    if interval <= 0:
        return True
    key = cache_key('performance_metric_write', path_hash, status_code, is_slow)
    try:
        return bool(redis_client.set(key, 1, ex=interval, nx=True))
    except Exception:
        return True


def write_performance_metric(request, response, path, ip, referer, user_agent, duration_ms, query_count, cache_status):
    path_hash = hashlib.md5(path.encode('utf-8')).hexdigest()
    status_code = getattr(response, 'status_code', 0) or 0
    slow_ms = env_int('PERFORMANCE_MONITOR_SLOW_MS', 400)
    is_slow = slow_ms > 0 and duration_ms >= slow_ms
    if not should_write_performance_metric(path, path_hash, status_code, is_slow):
        return
    try:
        PerformanceMetric.objects.create(
            method=short_text(request.method or 'GET', 8),
            path=short_text(path, 512),
            path_hash=path_hash,
            status_code=status_code,
            duration_ms=duration_ms,
            db_query_count=query_count,
            cache_status=cache_status,
            is_slow=is_slow,
            ip=ip or None,
            referer=short_text(referer, 1024),
            user_agent=short_text(user_agent, 512),
        )
    except Exception:
        pass


def is_authenticated_request(request):
    user = getattr(request, 'user', None)
    if user is None:
        return False
    authenticated = getattr(user, 'is_authenticated', False)
    return authenticated() if callable(authenticated) else bool(authenticated)


def is_page_cacheable_request(request):
    if page_cache_seconds() <= 0:
        return False
    if request.method not in ('GET', 'HEAD'):
        return False
    if is_authenticated_request(request):
        return False
    path = request.META.get('PATH_INFO', '/') or '/'
    if any(path.startswith(prefix) for prefix in PAGE_CACHE_EXCLUDED_PREFIXES):
        return False
    if path in ('/robots.txt', '/sitemap.xml', '/rss'):
        return False
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        return False
    return True


def page_cache_key(request):
    return cache_key(
        'page_cache_v1',
        request.META.get('HTTP_HOST', ''),
        request_path_with_query(request),
    )


def load_page_cache(request):
    if not is_page_cacheable_request(request):
        return None
    try:
        cached = redis_client.get(page_cache_key(request))
        if not cached:
            return None
        return json.loads(cached.decode() if isinstance(cached, bytes) else cached)
    except Exception:
        return None


def is_page_cacheable_response(response):
    if response.status_code != 200:
        return False
    if getattr(response, 'streaming', False):
        return False
    content_type = response.get('Content-Type', '')
    if 'text/html' not in content_type:
        return False
    if getattr(response, 'cookies', None):
        return False
    if response.has_header('Set-Cookie'):
        return False
    return hasattr(response, 'content')


def save_page_cache(request, response):
    if not is_page_cacheable_request(request) or not is_page_cacheable_response(response):
        return
    try:
        payload = {
            'content': response.content.decode('utf-8', 'ignore'),
            'content_type': response.get('Content-Type', 'text/html; charset=utf-8'),
        }
        redis_client.setex(page_cache_key(request), page_cache_seconds(), json.dumps(payload))
    except Exception:
        pass


def response_from_page_cache(cached):
    response = HttpResponse(
        cached.get('content', ''),
        content_type=cached.get('content_type') or 'text/html; charset=utf-8',
    )
    if env_bool('PAGE_CACHE_DEBUG_HEADER', False):
        response['X-MyBlog-Page-Cache'] = 'HIT'
    return response


def should_write_request_info(ip, path, user_agent, referer):
    interval = env_int('REQUEST_INFO_WRITE_INTERVAL_SECONDS', 60)
    if interval <= 0:
        return True

    key = cache_key('request_info_write', ip, path, user_agent, referer)
    try:
        return bool(redis_client.set(key, 1, ex=interval, nx=True))
    except Exception:
        return True


def lookup_region(ip):
    if not ip:
        return ''

    miss_key = 'ip_region_lookup_miss:{}'.format(ip)
    try:
        if redis_client.get(miss_key):
            return ''
    except Exception:
        pass

    timeout = env_float('IP_REGION_LOOKUP_TIMEOUT_SECONDS', 0.4)
    if timeout <= 0:
        return ''

    try:
        res = requests.get(
            'https://www.36ip.cn/?type=json&ip={}'.format(ip),
            timeout=timeout,
        )
        if res.status_code in (200, 201):
            return json.loads(res.text).get('data', '')
    except (requests.RequestException, ValueError, TypeError, KeyError):
        pass

    try:
        redis_client.setex(miss_key, env_int('IP_REGION_LOOKUP_MISS_SECONDS', 3600), 1)
    except Exception:
        pass
    return ''


class OnlineMiddleware(object):
    def __init__(self, get_response=None):
        self.get_response = get_response
        super().__init__()

    def __call__(self, request):
        start_time = time.time()
        start_queries = query_count_snapshot()
        cached_response = load_page_cache(request)
        if cached_response:
            response = response_from_page_cache(cached_response)
            cache_status = 'hit'
        else:
            response = self.get_response(request)
            cache_status = 'miss' if is_page_cacheable_request(request) else 'skip'
            save_page_cache(request, response)
            if env_bool('PAGE_CACHE_DEBUG_HEADER', False):
                response['X-MyBlog-Page-Cache'] = 'MISS'
        http_user_agent = request.META.get('HTTP_USER_AGENT', [])

        cast_time = time.time() - start_time
        duration_ms = int(round(cast_time * 1000))
        query_count = max(0, query_count_snapshot() - start_queries)
        ip = get_client_ip(request)
        referer = request.META.get('HTTP_REFERER', '')
        path = request_path_with_query(request)
        visitor = b'0'
        addr = ''

        if ip:
            try:
                with redis_client.pipeline(transaction=False) as p:
                    p.get('visitor')
                    p.hget('ip_address', ip)
                    p.get(ip)
                    visitor, addr, ip_flag = p.execute()
                    if not ip_flag:
                        p.incrby('visitor', 1)
                        p.setex(ip, 3600 * 24, 1)
                    if not addr:
                        addr = lookup_region(ip)
                        if addr:
                            p.hset('ip_address', ip, addr)
                    p.execute()
            except Exception:
                visitor = visitor or b'0'
                addr = ''

            if should_write_request_info(ip, path, http_user_agent, referer):
                try:
                    obj, _ = RequestInfo.objects.update_or_create(
                        request_ip=ip,
                        request_ua=http_user_agent,
                        request_region=_text(addr) or 'unkonwn',
                        request_path=path,
                        request_referer=referer
                    )
                    obj.request_times += 1
                    obj.save()
                except Exception:
                    pass

        if 'spider' in str(http_user_agent).lower():
            return response

        write_performance_metric(
            request, response, path, ip, referer, http_user_agent,
            duration_ms, query_count, cache_status,
        )

        if hasattr(response, 'content'):
            response.content = response.content.replace(b'<!!LOAD_TIMES!!>', str.encode(str(cast_time)[:5]))
            response.content = response.content.replace(b'<!!ip!!>', str.encode(ip))
            response.content = response.content.replace(b'<!!visitor!!>', str.encode(_text(visitor) or '0'))
            response.content = response.content.replace(b'<!!addr!!>', str.encode(_text(addr)))
        return response
