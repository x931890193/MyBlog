import time
import requests
import json

from MyBlog.utils import redis_client


class OnlineMiddleware(object):
    def __init__(self, get_response=None):
        self.get_response = get_response
        super().__init__()

    def __call__(self, request):
        redis_client.incrby('visitor', 1)
        start_time = time.time()
        response = self.get_response(request)
        http_user_agent = request.META.get('HTTP_USER_AGENT', [])

        cast_time = time.time() - start_time
        ip = request.META.get('HTTP_X_REAL_IP') or request.META.get('HTTP_X_FORWARDED_FOR') \
             or request.META.get('REMOTE_ADDR', '')
        visitor = redis_client.get('visitor')
        addr = redis_client.hget('ip_address', ip)
        if not addr:
            res = requests.get('https://www.36ip.cn/?type=json&ip={}'.format(ip))
            if res.status_code not in(200, 201):
                addr = ''
            else:
                addr = json.loads(res.text)['data']
                redis_client.hset('ip_address', ip, addr)
        if 'Spider' in http_user_agent or 'spider' in http_user_agent:
            return response
        response.content = response.content.replace(b'<!!LOAD_TIMES!!>', str.encode(str(cast_time)[:5]))
        response.content = response.content.replace(b'<!!ip!!>', str.encode(ip))
        response.content = response.content.replace(b'<!!visitor!!>', str.encode(visitor.decode()))
        response.content = response.content.replace(b'<!!addr!!>', str.encode(addr.decode() if isinstance(addr, bytes) else addr))
        return response

