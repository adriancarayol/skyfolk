# coding: utf-8
from django.db import models
from dash_services.models.services import Services
from dash_services.models import TriggerService


class Skyfolk(Services):
    """
        {{ th_skyfolk }} model to be adapted for the new service
    """
    # put whatever you need  here
    # eg title = models.CharField(max_length=80)
    # but keep at least this one
    trigger = models.ForeignKey(TriggerService, on_delete=models.CASCADE)

    class Meta:
        app_label = 'th_skyfolk'
        db_table = 'skyfolk_skyfolk'

    def __str__(self):
        return self.name

    def show(self):
        return "My {{ class_name }} %s" % self.name
