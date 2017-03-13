import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Timeline, EventTimeline
from publications.models import Publication
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def handle_new_user(sender, instance, created, **kwargs):
    if created:
        logger.info("POST_SAVE : Create Timeline, User : %s" % instance)
        Timeline.objects.create(timeline_owner=instance)


@receiver(post_save, sender=EventTimeline)
def handle_new_event(sender, instance, created, **kwargs):
    if created:
        timeline = Timeline.objects.get(timeline_owner=instance.author)
        timeline.events.add(instance)
        logger.info("POST SAVE : New event added in timeline : %s " % instance.author)

    if not created:
        instance.created = datetime.now()


@receiver(post_save, sender=Publication)
def handle_new_publication(sender, instance, created, **kwargs):
    if created:
        EventTimeline.objects.create(author=instance.author, publication=instance)
        logger.info("POST SAVE : New event created by user : %s " % instance.author)
