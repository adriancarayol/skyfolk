#!/usr/bin/env python
# coding: utf-8
from __future__ import unicode_literals
# django
from concurrent.futures import ThreadPoolExecutor

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q
# trigger happy
from dash_services.models import TriggerService
from dash_services.publish import Pub
from logging import getLogger

# create logger
logger = getLogger('django_th.trigger_happy')


class Command(BaseCommand):
    help = 'Trigger all the services and publish the data coming from the cache'

    def handle(self, *args, **options):
        """
            get all the triggers that need to be handled
        """
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

        with ThreadPoolExecutor(max_workers=settings.DJANGO_TH.get('processes')) as executor:
            p = Pub()
            for t, result in zip(trigger, executor.map(p.publishing, trigger, timeout=60)):
                logger.info('Command publish for trigger: {}'.format(t))
