"""
WSGI config for MyBlog project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os

from MyBlog.env import configure_runtime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MyBlog.settings")
configure_runtime()

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
