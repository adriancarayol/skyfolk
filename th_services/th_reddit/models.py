# coding: utf-8
from django.db import models
from dash_services.models.services import Services
from dash_services.models import TriggerService


class Reddit(Services):

    """
        reddit model to be adapted for the new service
    """
    # put whatever you need  here
    # eg title = models.CharField(max_length=80)
    # but keep at least this one
    subreddit = models.CharField(max_length=80)
    share_link = models.BooleanField(default=False)
    trigger = models.ForeignKey(TriggerService, on_delete=models.CASCADE)

    class Meta:
        app_label = 'th_services.th_reddit'
        db_table = 'skyfolk_reddit'

    def __str__(self):
        return self.subreddit

    def show(self):
        return "My Reddit %s" % self.subreddit