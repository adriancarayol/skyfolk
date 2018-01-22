# coding: utf-8
from django.db import models
from skyfolk.models.services import Services
from skyfolk.models import TriggerService


class Todoist(Services):

    """
        todoist model to be adapted for the new service
    """
    trigger = models.ForeignKey(TriggerService)

    class Meta:
        app_label = 'th_todoist'
        db_table = 'skyfolk_todoist'

    def show(self):
        """

        :return: string representing object
        """
        return "My Todoist %s" % self.name

    def __str__(self):
        return "%s" % self.name
