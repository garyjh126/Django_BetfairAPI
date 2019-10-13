from __future__ import absolute_import

import os

from celery import Celery

from django.conf import settings  # noqa


# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'betfair.settings')

if not os.environ.get('REDIS_HOST'):
    REDIS_HOST = '127.0.0.1'
else:
    REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PASSWORD = 'foobared' if not os.environ.get('REDIS_PASSWORD') else os.environ.get('REDIS_PASSWORD')

app = Celery('betfair')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
