# coding: utf-8
from django.db import models
from dash_services.models.services import Services
from dash_services.models import TriggerService
import uuid


class Rss(Services):
    """
        Model for RSS Service
    """
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    url = models.URLField(max_length=255)
    trigger = models.ForeignKey(TriggerService)

    class Meta:
        app_label = 'th_rss'
        db_table = 'skyfolk_rss'

    def show(self):
        """

        :return: string representing object
        """
        return "Services RSS %s %s" % (self.url, self.trigger)

    def __str__(self):
        return "%s" % self.url
