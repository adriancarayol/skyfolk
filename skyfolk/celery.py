from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

from django.conf import settings

# Cargamos SECRET_KEY
def get_env_variable(var_name):
    '''Intenta leer una variable de entorno'''
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = "Set the %s environment variable" % var_name
        raise ImproperlyConfigured(error_msg)


DJANGO_SETTINGS_MODULE = get_env_variable('DJANGO_SETTINGS_MODULE')

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


@app.task(bind=True)
def debug_task(self):
        print('Request: {0!r}'.format(self.request))
