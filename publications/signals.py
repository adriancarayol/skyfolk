import logging
import os
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save, post_delete
from .models import Publication, ExtraContent


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@receiver(post_save, sender=Publication, dispatch_uid='publication_save')
def publication_handler(sender, instance, created, **kwargs):
    if created:
        logger.info('New comment by: {} with content: {}'.format(instance.author, instance.content))
    if instance.extra_content: # Para publicaciones editadas
        ExtraContent.objects.filter(publication=instance.id).exclude(url=instance.extra_content.url).delete()
    else:
        ExtraContent.objects.filter(publication=instance.id).delete()


def _delete_image(path):
	"""
	Delete image (publication) from filesystem
	"""
	if os.path.isfile(path):
		os.remove(path)


@receiver(post_delete, sender=Publication)
def publication_deleted(sender, instance, *args, **kwargs):
	if instance.image:
		_delete_image(instance.image.path)