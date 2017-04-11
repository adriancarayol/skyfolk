from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from .models import Publication, ExtraContent
import logging


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


