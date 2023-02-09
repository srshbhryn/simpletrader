import os

from celery import Celery
from .settings import CELERY_BROKER

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'simpletrader.settings')

app = Celery(
    'simpletrader',
    broker=CELERY_BROKER,
    backend='rpc',
)

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
