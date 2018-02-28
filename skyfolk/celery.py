from __future__ import absolute_import, unicode_literals
import os
import django
from celery import Celery
from celery.schedules import crontab
from django.conf import settings
from kombu import Exchange, Queue

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyfolk.settings.develop')

app = Celery('skyfolk')

app.config_from_object('skyfolk.celeryconf')

app.autodiscover_tasks()

app.conf.task_default_queue = 'medium'

app.conf.task_queues = (
    Queue('high', Exchange('high'), routing_key='high'),
    Queue('medium', Exchange('medium'), routing_key='medium'),
    Queue('low', Exchange('low'), routing_key='low'),
    Queue('fetch', Exchange('fetch'), routing_key='fetch'),
    Queue('swarm', Exchange('swarm'), routing_key='swarm'),
    Queue('clean', Exchange('clean'), routing_key='clean'),
    Queue('background', Exchange('background'), routing_key='background'),
)

app.conf.beat_schedule = {
    'deleted-publication': {
        'task': 'tasks.clean_deleted_publications',
        'schedule': crontab(minute=0, hour=2),
        'options': {'queue': 'clean'}
    },
    'deleted-photo-publication': {
        'task': 'tasks.clean_deleted_photo_publications',
        'schedule': crontab(minute=0, hour=2),
        'options': {'queue': 'clean'}
    },
    'recommendations-via-email': {
        'task': 'tasks.send_recommendation_via_email',
        'schedule': crontab(minute=0, hour='*/15'),
        'options': {'queue': 'background'}
    },
    'read_services': {
        'task': 'tasks.read_services',
        'schedule': crontab('*/10'),
        'options': {'queue': 'low'}
    },
    'publish_services': {
        'task': 'tasks.publish_services',
        'schedule': crontab('*/15'),
        'options': {'queue': 'low'}
    },
    'recycle_services': {
        'task': 'tasks.recycle_services',
        'schedule': crontab('*/40'),
        'options': {'queue': 'low'}
    }
}

"""
Celery tiene problemas a la hora de descubrir
subaplicaciones dentro de aplicaciones,
por ejemplo 'dash.contrib.layouts.profile'
es necesario llamar a setup() para cargar
la configuracion de las aplicaciones necesaria
"""
if not hasattr(django, 'apps'):
    django.setup()

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

