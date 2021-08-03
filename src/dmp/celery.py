from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dmp.settings')

app = Celery('dmp')

app.config_from_object('django.conf:settings',namespace='CELERY')

app.conf.timezone = 'America/Santiago'

app.autodiscover_tasks(lambda:settings.INSTALLED_APPS)

# app.conf.beat_schedule = {
#     'check-threshold-4': {
#         'task': 'umbral_4',
#         'schedule' : crontab(minute='*/1')
#         # 'schedule' : crontab(hour='*/24')
#     },
# }

app.conf.beat_schedule = {
    'check-threshold-2': {
        'task': 'umbral_2',
        'enable': True,
        'schedule' : crontab(minute='*/1')
        # 'schedule' : crontab(hour='*/24')
    },

    'check-threshold-3': {
        'task': 'umbral_3',
        'enable': True,
        'schedule' : crontab(minute='*/1')
        # 'schedule' : crontab(hour='*/24')
    },
    
}
