import logging
import os
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete
from .models import Publication, ExtraContent
from user_profile.models import NodeProfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@receiver(post_save, sender=Publication, dispatch_uid='publication_save')
def publication_handler(sender, instance, created, **kwargs):
    if created:
        logger.info('New comment by: {} with content: {}'.format(instance.author, instance.content))
        n = NodeProfile.nodes.get(user_id=instance.author.id)
        m = NodeProfile.nodes.get(user_id=instance.board_owner.id)

        if n.uid != m.uid:
            rel = n.follow.relationship(m)
            if rel:
                rel.weight = rel.weight + 1
                rel.save()

    if instance.deleted:
        logger.info('Publication soft deleted, with content: {}'.format(instance.content))
        n = NodeProfile.nodes.get(user_id=instance.author.id)
        m = NodeProfile.nodes.get(user_id=instance.board_owner.id)

        if n.uid != m.uid:
            rel = n.follow.relationship(m)
            if rel:
                rel.weight = rel.weight - 1
                rel.save()

        if instance.has_extra_content():  # Para publicaciones editadas
            ExtraContent.objects.filter(publication=instance.id).exclude(url=instance.extra_content.url).delete()
        else:
            ExtraContent.objects.filter(publication=instance.id).delete()
