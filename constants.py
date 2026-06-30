# coding=utf-8
from __future__ import unicode_literals

import os
import socket

from MyBlog.env import env, env_bool


hostname = socket.gethostname()

QINIU_ACCESS_KEY = env('QINIU_ACCESS_KEY', '')
QINIU_SECRET_KEY = env('QINIU_SECRET_KEY', '')
QINIU_BUCKET_NAME = env('QINIU_BUCKET_NAME', '')
QINIU_DOMAIN = env('QINIU_BUCKET_DOMAIN', '')
QINIU_USE_SSL = env_bool('QINIU_SECURE_URL', True)

LOG_MAX_BYTES = 1024 * 1024 * 20
LOG_BACKUP_COUNT = 5

REDIS_HOST = env('REDIS_HOST', '127.0.0.1')
REDIS_PORT = int(env('REDIS_PORT', '6379'))
REDIS_DB = int(env('REDIS_DB', '0'))
REDIS_PASSWD = env('REDIS_PASSWD', '')

DEBUG = env_bool('DEBUG', False)
DB_HOST = env('DB_HOST', env('MYSQL_HOST', '127.0.0.1'))
MONGO_URI = env('MONGO_URI', 'mongodb://127.0.0.1:27017')
MONGODB_NAME = env('MONGODB_NAME', 'blog')
LOG_FILE_PATH = env('LOG_FILE_PATH', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log', 'myblog.log'))

MASTER_DATABASE_CONN_MAX_AGE = 60
