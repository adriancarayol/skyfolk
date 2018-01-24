from celery.utils.log import get_task_logger
from skyfolk.celery import app
from skyfolk.publish import Pub
from skyfolk.read import Read
from skyfolk.models import TriggerService
from multiprocessing import Pool, TimeoutError
from skyfolk.recycle import recycle

logger = get_task_logger(__name__)

@app.task(name='tasks.read_services', ignore_result=True)
def read_services():
    pass
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
    try:
    	with Pool(processes=settings.DJANGO_TH.get('processes')) as pool:
			r = Read()
            result = pool.map_async(r.reading, trigger)
            result.get(timeout=60)
    except TimeoutError as e:
        logger.warning(e)

@app.task(name='tasks.publish_services', ignore_result=True)
def publish_services():
    pass
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
    try:
    	with Pool(processes=settings.DJANGO_TH.get('processes')) as pool:
            p = Pub()
            result = pool.map_async(p.publishing, trigger)
            result.get(timeout=60)
	except TimeoutError as e:
        logger.warning(e)

@app.task(name='tasks.recycle_services', ignore_result=True)
def recycle_services():
	recycle()