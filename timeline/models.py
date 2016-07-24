from django.db import models
from django.contrib.auth.models import User
from user_profile.models import UserProfile
from publications.models import Publication
from model_utils import Choices

# TODO
class TimelineManager(models.Manager):
    pass


class Timeline(models.Model):
    publication = models.ForeignKey(Publication, null=True, related_name='publications')
    author = models.ForeignKey(UserProfile, related_name='from_timeline', null=True)
    profile = models.ForeignKey(UserProfile, related_name='to_timeline')
    insertion_date = models.DateField(auto_now_add=True)
    verb = models.CharField(max_length=255, null=True)
    TYPES = Choices('publication', 'new_relation')
    type = models.CharField(choices=TYPES, default=TYPES.publication, max_length=20)

    objects = TimelineManager()

    class Meta:
        ordering = ('-insertion_date', )

    def __unicode__(self):
        if self.publication.content:
            return self.publication.content
        if self.verb:
            return self.verb

    # Mostrar contenido en formato string.
    def __str__(self):
        return self.self.__unicode__()