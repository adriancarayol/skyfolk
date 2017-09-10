import logging

from badgify.models import Award
from django.db.models.signals import post_save
from django.dispatch import receiver

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@receiver(post_save, sender=Award, dispatch_uid='award_save')
def awards_handler(sender, instance, created, **kwargs):
    logger.info('User: {} ha logrado un nuevo logro: {}'.format(instance.user, instance.badge))
