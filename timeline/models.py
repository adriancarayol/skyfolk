from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from model_utils import Choices

from publications.models import Publication
from user_profile.models import UserProfile


# TODO
class TimelineManager(models.Manager):
    # Funciones timeline
    def get_timeline(self, timelinepk):
        return self.get(pk=timelinepk)

    def remove_timeline(self, timelinepk, userpk):
        timeline = self.get(pk=timelinepk)
        try:
            pub = timeline.publication
        except ObjectDoesNotExist:
            pub = None
        if pub:
            pub.user_share_me.remove(userpk)
        timeline.delete()

    def get_author_timeline(self, authorpk):
        timeline = self.filter(author=authorpk).order_by('insertion_date').reverse()

        return timeline


class Timeline(models.Model):
    publication = models.ForeignKey(Publication, null=True, related_name='publications')
    author = models.ForeignKey(UserProfile, related_name='from_timeline', null=True)
    profile = models.ForeignKey(UserProfile, related_name='to_timeline')
    insertion_date = models.DateTimeField(auto_now_add=True)
    verb = models.CharField(max_length=255, null=True)
    TYPES = Choices('publication', 'new_relation')
    type = models.CharField(choices=TYPES, default=TYPES.publication, max_length=20)

    objects = TimelineManager()

    class Meta:
        ordering = ('-insertion_date',)

    def __unicode__(self):
        if self.publication.content:
            return self.publication.content
        if self.verb:
            return self.verb

    # Mostrar contenido en formato string.
    def __str__(self):
        return self.self.__unicode__()
