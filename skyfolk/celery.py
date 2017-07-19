from __future__ import absolute_import, unicode_literals
from celery import Celery
from django.conf import settings
from celery.schedules import crontab

# set the default Django settings module for the 'celery' program.
#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skyfolk.settings.develop')

app = Celery('skyfolk')

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.beat_schedule = {
    'deleted-publication': {
        'task': 'tasks.clean_deleted_publications',
        'schedule': crontab(minute=0, hour=0),
    },
    'deleted-photo-publication': {
        'task': 'tasks.clean_deleted_photo_publications',
        'schedule': crontab(minute=0, hour=2),
    }
}

@app.task(bind=True)
def debug_task(self):
        print('Request: {0!r}'.format(self.request))
