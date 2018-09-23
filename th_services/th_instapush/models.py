# coding: utf-8
from django.db import models
from dash_services.models.services import Services
from dash_services.models import TriggerService


class Instapush(Services):
    """

        wallabag model to be adapted for the new service
        to store url in your account

    """
    app_id = models.CharField(max_length=255)
    app_secret = models.CharField(max_length=255)
    event_name = models.CharField(max_length=255)
    tracker_name = models.CharField(max_length=80)
    trigger = models.ForeignKey(TriggerService, on_delete=models.CASCADE)

    class Meta:
        app_label = 'th_instapush'
        db_table = 'skyfolk_instapush'

    def show(self):
        """

        string representing object
        """
        return "My Instapush %s" % self.name

    def __str__(self):
        return "%s" % self.name
