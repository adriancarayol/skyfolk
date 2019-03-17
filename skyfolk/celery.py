from __future__ import absolute_import, unicode_literals
import os
import django
from celery import Celery
from celery.schedules import crontab
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
        'schedule': crontab(hour=7, minute=30, day_of_week=1),
        'options': {'queue': 'background'}
    },
    'periodic_update_external_services': {
        'task': 'tasks.periodic_update_external_services',
        'schedule': crontab(minute=1),
        'options': {'queue': 'low'}
    },
    'periodic_checking_ranks': {
        'task': 'tasks.periodic_checking_ranks',
        'schedule': crontab(hour=1),
        'options': {'queue': 'background'}
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
