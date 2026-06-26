# coding=utf-8
from __future__ import unicode_literals

import os


def project_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_env(path=None):
    path = path or os.environ.get('MYBLOG_ENV_FILE') or os.path.join(project_root(), '.env')
    if not os.path.exists(path):
        return
    with open(path) as env_file:
        for line in env_file:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)


def env(name, default=None):
    return os.environ.get(name, default)


def env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in ('1', 'true', 'yes', 'on')


def env_list(name, default=None, separator=','):
    value = os.environ.get(name)
    if value is None:
        return default or []
    return [item.strip() for item in value.split(separator) if item.strip()]


def configure_mysql():
    import pymysql

    pymysql.install_as_MySQLdb()
    try:
        from django.db.backends.mysql.base import DatabaseWrapper
    except Exception:
        return
    if getattr(DatabaseWrapper, '_myblog_utf8mb4_configured', False):
        return

    original_get_connection_params = DatabaseWrapper.get_connection_params

    def get_connection_params(self):
        params = original_get_connection_params(self)
        options = self.settings_dict.get('OPTIONS') or {}
        if 'charset' not in options and params.get('charset') == 'utf8':
            params['charset'] = 'utf8mb4'
        params.setdefault('init_command', 'SET NAMES utf8mb4')
        return params

    DatabaseWrapper.get_connection_params = get_connection_params
    DatabaseWrapper._myblog_utf8mb4_configured = True


def configure_runtime():
    load_env()
    configure_mysql()
