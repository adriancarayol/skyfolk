# coding: utf-8
from django.db import models
from dash_services.models.services import Services
from dash_services.models import TriggerService


class Tumblr(Services):

    """
        tumblr model to be adapted for the new service
    """
    blogname = models.CharField(max_length=80)
    tag = models.CharField(max_length=80, blank=True)
    trigger = models.ForeignKey(TriggerService, on_delete=models.CASCADE)

    class Meta:
        app_label = 'th_tumblr'
        db_table = 'skyfolk_tumblr'

    def __str__(self):
        return self.blogname

    def show(self):
        return "My Tumblr %s" % self.blogname
