import logging

from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from guardian.shortcuts import assign_perm

from notifications.models import Notification
from .models import UserGroups, RequestGroup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@receiver(post_save, sender=UserGroups)
def handle_new_group(sender, instance, created, **kwargs):
    if created:  # Primera vez que se crea el usuario, creamos Perfil y Nodo
        assign_perm('view_notification', instance.owner, instance)
        assign_perm('can_publish', instance.owner, instance)
        assign_perm('change_description', instance.owner, instance)
        assign_perm('delete_publication', instance.owner, instance)
        assign_perm('delete_image', instance.owner, instance)
        assign_perm('kick_member', instance.owner, instance)
        assign_perm('ban_member', instance.owner, instance)
        assign_perm('modify_notification', instance.owner, instance)


@receiver(post_delete, sender=RequestGroup)
def handle_delete_request(sender, instance, *args, **kwargs):
    Notification.objects.filter(action_object_object_id=instance.id,
                                action_object_content_type=ContentType.objects.get_for_model(instance)).delete()
