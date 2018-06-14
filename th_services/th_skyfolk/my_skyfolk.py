# coding: utf-8
# add here the call of any native lib of python like datetime etc.


from django.core.cache import caches
from logging import getLogger

from dash_services.models import update_result
from publications.models import Publication
# django_th classes
from dash_services.services.services import ServicesMgr

logger = getLogger('django_th.trigger_happy')
cache = caches['django_th']


class ServiceSkyfolk(ServicesMgr):
    def save_data(self, trigger_id, **data):
        """
            let's save the data
            :param trigger_id: trigger ID from which to save data
            :param data: the data to check to be used and save
            :type trigger_id: int
            :type data:  dict
            :return: the status of the save statement
            :rtype: boolean
        """
        from th_services.th_skyfolk.models import Skyfolk

        status = False

        title, content = super(ServiceSkyfolk, self).save_data(trigger_id, **data)
        trigger = Skyfolk.objects.get(trigger_id=trigger_id)

        content = '<b>' + title + '</b>\n' + content
        try:
            Publication.objects.create(content=content, author=trigger.trigger.user, board_owner=trigger.trigger.user)
            status = True
        except Exception as e:
            update_result(trigger_id, msg=e, status=False)
            logger.info(e)

        return status
