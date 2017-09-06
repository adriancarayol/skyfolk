from __future__ import absolute_import, unicode_literals
import skyfolk.celeryconf as celeryconf
from celery import Celery
from celery.schedules import crontab
from django.conf import settings
from kombu import Exchange, Queue

# set the default Django settings module for the 'celery' program.
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyfolk.settings.develop')

app = Celery('skyfolk')

app.config_from_object(celeryconf)

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

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

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
    }
}


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))