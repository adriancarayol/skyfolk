import requests
from skyfolk.celery import app
from celery.utils.log import get_task_logger
from celery import group
from dash.models import DashboardEntry

logger = get_task_logger(__name__)


@app.task(name='tasks.periodic_update_external_services')
def periodic_update_external_services():
    """
    Update external services
    """
    all_user_service_ids = DashboardEntry.objects.filter(user__is_active=True,
                                                         plugin_uid__istartswith='service').values_list('id', flat=True)
    group(update_external_services.s(row) for row in all_user_service_ids).apply_async()


@app.task(ignore_result=False)
def update_external_services(user_service_id):
    data = {'id': user_service_id}
    url = "http://go_skyfolk:1800/update/"
    try:
        response = requests.post(url=url, data=data)
        return response.status_code
    except requests.exceptions.RequestException as e:
        logger.warn(e)

    return 500
