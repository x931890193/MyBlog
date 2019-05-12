# encoding: utf-8
"""
Create on: 2019-01-30 下午5:45
author: sato
mail: ysudqfs@163.com
life is short, you need python
"""
import redis
import requests
import json
from constants import REDIS_HOST, REDIS_PORT, REDIS_DB

redis_client = redis.Redis(REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)


def get_video_curl(_id, ty):
    url = "http://music.163.com/api/mv/detail?id=%s&type=mp4" % _id
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
    }
    html = requests.get(url, headers=headers)
    if html.status_code not in (200, 201):
        print('网络错误!')
        return ''
    url = json.loads(html.text)['data']['brs']['%s' % ty]
    return url


def record_visitor():

    visitor = redis_client.get('visitor')
    if visitor:
        visitor_num = int(visitor)
        try:
            with open('visitor_num.txt', 'w+') as f:
                num = f.read()
                if not num:
                    num = 0
                if visitor_num > int(num):
                    f.write(str(visitor_num))
        except Exception as e:
            print(e)


def record_ip():

    ip_info = redis_client.hgetall("ip_address")
    ip_info = {k.decode(): v.decode() for k, v in ip_info.items()}
    try:
        with open('ip_address.json', 'w+') as f:
            json.dump(ip_info, fp=f)
    except Exception as e:
        print(e)