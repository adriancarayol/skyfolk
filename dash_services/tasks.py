from celery.utils.log import get_task_logger
from django.contrib.auth.models import User
from skyfolk.celery import app
from django.conf import settings
import concurrent.futures
from dash_services.models import TriggerService
from dash_services.read import Read
from dash_services.publish import Pub
from django.db.models import Q
from celery import group

logger = get_task_logger(__name__)


@app.task(name='tasks.read_services', ignore_result=True)
def read_services():
    help = 'Trigger all the services and put them in cache'

    from django.db import connection
    connection.close()
    failed_tries = settings.DJANGO_TH.get('failed_tries', 10)
    trigger = TriggerService.objects.filter(
        Q(provider_failed__lte=failed_tries) |
        Q(consumer_failed__lte=failed_tries),
        status=True,
        user__is_active=True,
        provider__name__status=True,
        consumer__name__status=True,
    ).select_related('consumer__name', 'provider__name')
     
    for t in trigger:
        r = Read()
        result = r.reading(t)

@app.task(name="tasks.publish_services", ignore_result=True)
def publish_services():
    help = 'Trigger all the services and publish the data coming from the cache'

    from django.db import connection
    connection.close()
    failed_tries = settings.DJANGO_TH.get('failed_tries', 10)
    trigger = TriggerService.objects.filter(
        Q(provider_failed__lte=failed_tries) |
        Q(consumer_failed__lte=failed_tries),
        status=True,
        user__is_active=True,
        provider__name__status=True,
        consumer__name__status=True,
    ).select_related('consumer__name', 'provider__name')
    
    for t in trigger:
        p = Pub()
        result = p.publishing(t)


@app.task(name="tasks.recycle_services", ignore_result=True)
def recycle_services():
    from dash_services.recycle import recycle
    recycle()