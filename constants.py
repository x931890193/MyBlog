# encoding: utf-8
"""
Create on: 2019-01-17 下午5:12
author: sato
mail: ysudqfs@163.com
life is short, you need python
"""
import socket

hostname = socket.gethostname()

QINIU_ACCESS_KEY = ''
QINIU_SECRET_KEY = ''
QINIU_BUCKET_NAME = ''
QINIU_DOMAIN = 'https://cdn.mongona.com'
QINIU_USE_SSL = True

LOG_FILE_PATH = '/data/logs/blog.log'
LOG_MAX_BYTES = 1024 * 1024 * 1024 * 1024
LOG_BACKUP_COUNT = 1

REDIS_HOST = '127.0.0.1' if hostname == 'iZ2ze73gz63uq4erkj5ilxZ' else ''
REDIS_PORT = 6379
REDIS_DB = 0

if hostname in ['satodeMacBook-Pro.local', 'Deepin']:
    DEBUG = True
    DB_HOST = ''


else:
    DEBUG = False
    DB_HOST = ''