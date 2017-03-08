from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q

from publications.models import Publication
from django.utils.translation import gettext as _


# TODO
class TimelineManager(models.Manager):
    # Funciones timeline
    def get_timeline(self, timelinepk):
        return self.get(pk=timelinepk)

    def get_user_profile_events(self, user_pk):
        timeline = self.get(timeline_owner=user_pk)

        events = timeline.events.all()

        for e in events:
            if e.publication:
                reply = Publication.objects.filter(parent=e.publication.pk, deleted=False).order_by('-created')
                e.replies = reply

        return events


class EventTimeline(models.Model):
    """
    Representa un evento en el timeline
    """
    EVENT_CHOICES = (
        (1, _("publication")),
        (2, _("new_relation")),
        (3, _("notice")),
        (4, _("relevant")),
        (5, _("image"))
    )
    publication = models.ForeignKey(Publication, related_name='publication', null=True)
    event_type = models.IntegerField(choices=EVENT_CHOICES, default=1)
    author = models.ForeignKey(User, related_name='owner_event', null=True)
    created = models.DateTimeField(auto_now_add=True)


class Timeline(models.Model):
    events = models.ManyToManyField(EventTimeline, related_name='events')
    timeline_owner = models.OneToOneField(User, related_name='owner_timeline')
    objects = TimelineManager()
