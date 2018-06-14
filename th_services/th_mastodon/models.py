# coding: utf-8
from django.db import models
from dash_services.models import TriggerService
from dash_services.models.services import Services
from django.utils.translation import ugettext_lazy as _

SCOPES = (
     ('home', _('Home')),
     ('public', _('Public'))
)


class Mastodon(Services):
    """
        Model for Mastodon Service
    """
    timeline = models.CharField(max_length=10, default="home", choices=SCOPES)
    tooter = models.CharField(max_length=80, null=True, blank=True)
    fav = models.BooleanField(default=False)
    tag = models.CharField(max_length=80, null=True, blank=True)
    since_id = models.BigIntegerField(null=True, blank=True)
    max_id = models.BigIntegerField(null=True, blank=True)
    count = models.IntegerField(null=True, blank=True)
    trigger = models.ForeignKey(TriggerService)

    class Meta:
        app_label = 'th_services.th_mastodon'
        db_table = 'skyfolk_mastodon'

    def show(self):
        """

        :return: string representing object
        """
        return "My Mastodon %s %s" % (self.timeline, self.trigger)

    def __str__(self):
        return "%s" % self.timeline
