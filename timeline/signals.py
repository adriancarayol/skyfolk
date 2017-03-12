import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Timeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def handle_new_user(sender, instance, created, **kwargs):
    if created:
        logger.info("POST_SAVE : Create Timeline, User : %s" % instance)
        Timeline.objects.create(timeline_owner=instance)