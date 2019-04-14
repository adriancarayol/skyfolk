import json
import logging

from channels.layers import get_channel_layer
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.http import Http404
from django.template.loader import render_to_string
from guardian.shortcuts import assign_perm

from notifications.models import Notification
from .models import UserGroups, RequestGroup, LikeGroup, GroupTheme
from asgiref.sync import async_to_sync

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

channel_layer = get_channel_layer()


@receiver(post_save, sender=UserGroups)
def handle_new_group(sender, instance, created, **kwargs):
    if created:
        assign_perm("view_notification", instance.owner, instance)
        assign_perm("can_publish", instance.owner, instance)
        assign_perm("change_description", instance.owner, instance)
        assign_perm("delete_publication", instance.owner, instance)
        assign_perm("delete_image", instance.owner, instance)
        assign_perm("kick_member", instance.owner, instance)
        assign_perm("ban_member", instance.owner, instance)
        assign_perm("modify_notification", instance.owner, instance)


@receiver(post_delete, sender=RequestGroup)
def handle_delete_request(sender, instance, *args, **kwargs):
    Notification.objects.filter(
        action_object_object_id=instance.id,
        action_object_content_type=ContentType.objects.get_for_model(instance),
    ).delete()


@receiver(post_save, sender=GroupTheme)
def handle_new_theme(sender, instance, created, *args, **kwargs):
    if created:
        theme = render_to_string("groups/group_themes.html", {"themes": [instance]})
        group = UserGroups.objects.get(id=instance.board_group_id)
        data = {"theme": theme, "type": "theme", "id": instance.id}

        async_to_sync(channel_layer.group_send)(
            group.group_channel, {"type": "new_publication", "message": data}
        )
