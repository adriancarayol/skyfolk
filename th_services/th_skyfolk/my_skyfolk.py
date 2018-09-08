# coding: utf-8
# add here the call of any native lib of python like datetime etc.
import arrow

from django.conf import settings
from django.core.cache import caches
from logging import getLogger

from dash_services.models import update_result
from publications.models import Publication
# django_th classes
from dash_services.services.services import ServicesMgr
from .models import Skyfolk
from publications.models import Publication
logger = getLogger('django_th.trigger_happy')
cache = caches['django_th']


class ServiceSkyfolk(ServicesMgr):

    def read_data(self, **kwargs):
        """
            get the data from the service
            as the pocket service does not have any date
            in its API linked to the note,
            add the triggered date to the dict data
            thus the service will be triggered when data will be found
            :param kwargs: contain keyword args : trigger_id at least
            :type kwargs: dict
            :rtype: list
        """
        trigger_id = kwargs.get('trigger_id')
        trigger = Skyfolk.objects.get(trigger_id=trigger_id)
        date_triggered = arrow.get(kwargs.get('date_triggered'))
        data = list()
        publications = Publication.objects.filter(level__lte=1, 
                        author=trigger.trigger.user, 
                        board_owner=trigger.trigger.user).order_by('-created')[:5]

        for publication in publications:
            title = 'From Skyfolk ' + publication.author.username
            created = arrow.get(publication.created).to(settings.TIME_ZONE)

            if date_triggered is not None and created is not None \
                    and created >= date_triggered:
                body = publication.content
                data.append({'title': title, 'content': body})
                self.send_digest_event(trigger_id, title, '')

        cache.set('th_services.th_skyfolk_' + str(trigger_id), data)

        return data

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

        content = '<b>' + title + '</b>: ' + content
        try:
            Publication.objects.create(content=content, author=trigger.trigger.user, board_owner=trigger.trigger.user)
            status = True
        except Exception as e:
            update_result(trigger_id, msg=e, status=False)
            logger.info(e)

        return status
