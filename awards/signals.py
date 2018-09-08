import logging

from badgify.models import Award
from django.db.models.signals import post_save
from django.dispatch import receiver
from notifications.signals import notify

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@receiver(post_save, sender=Award, dispatch_uid='award_save')
def awards_handler(sender, instance, created, **kwargs):
	notify.send(instance.user, actor=instance.user.username,
		recipient=instance.user,
		verb=u'¡Nuevo logro conseguido!',
		description=u'Has obtenido el logro: {} (+{} puntos)'.format(instance.badge.name, instance.badge.points))
	logger.info('User: {} ha logrado un nuevo logro: {}'.format(instance.user, instance.badge))
