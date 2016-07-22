from django.db import models
from django.contrib.auth.models import User
from user_profile.models import UserProfile
from publications.models import Publication

# TODO
class TimelineManager(models.Manager):
    pass


class Timeline(models.Model):
    publication = models.ForeignKey(Publication, null=True, related_name='publications')
    author = models.ForeignKey(UserProfile, related_name='from_timeline', null=True)
    profile = models.ForeignKey(UserProfile, related_name='to_timeline')
    insertion_date = models.DateField(auto_now_add=True)

    objects = TimelineManager()
    # Mostrar contenido en formato string.
    def __str__(self):
        return self.publication.content

    def __unicode__(self):
        return self.publication.content