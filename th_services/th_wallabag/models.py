# coding: utf-8
from django.db import models
from dash_services.models.services import Services
from dash_services.models import TriggerService


class Wallabag(Services):
    """

        wallabag model to be adapted for the new service
        to store url in your account

    """
    url = models.URLField(max_length=255)
    title = models.CharField(max_length=80, blank=True)
    tag = models.CharField(max_length=80, blank=True)
    trigger = models.ForeignKey(TriggerService)

    class Meta:
        app_label = 'th_services.th_wallabag'
        db_table = 'skyfolk_wallabag'

    def show(self):
        """

        :return: string representing object
        """
        return "My Wallabag %s" % self.url

    def __str__(self):
        return "%s" % self.url
