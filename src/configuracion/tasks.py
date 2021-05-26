from __future__ import absolute_import, unicode_literals
from celery import shared_task
from celery.decorators import task

@shared_task
def umbral_1(umbral, doc):
    pass

@shared_task
def umbral_2(umbral, doc):
    pass

@shared_task
def umbral_3(umbral, doc):
    pass

@shared_task
def umbral_4(umbral, doc):
    pass

@task(name="send_alert_email")
def send_mail(user, message):
    pass