import logging

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.http import Http404
from guardian.shortcuts import assign_perm
from django.contrib.auth.models import User, Group
from notifications.models import Notification
from user_groups.node_models import NodeGroup
from user_profile.node_models import NodeProfile
from .models import UserGroups, RequestGroup, LikeGroup

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


@receiver(m2m_changed, sender=User.groups.through)
def user_group_changed_handler(sender, instance, action, **kwargs):
    if isinstance(instance, UserGroups):
        pk_set = kwargs.pop('pk_set', [])
        try:
            g = NodeGroup.nodes.get(group_id=instance.group_ptr_id)
        except NodeGroup.DoesNotExist:
            raise ObjectDoesNotExist

        if action == 'post_add':
            for p in pk_set:
                try:
                    n = NodeProfile.nodes.get(user_id=p)
                except (NodeGroup, NodeProfile) as e:
                    raise ObjectDoesNotExist

                g.members.connect(n)

        elif action == 'post_remove':
            for p in pk_set:
                try:
                    n = NodeProfile.nodes.get(user_id=p)
                except (NodeGroup, NodeProfile) as e:
                    raise Http404

                g.members.disconnect(n)

@receiver(post_save, sender=LikeGroup)
def handle_new_like(sender, instance, created, *args, **kwargs):
    if created:
        try:
            g = NodeGroup.nodes.get(group_id=instance.to_like.id)
            n = NodeProfile.nodes.get(user_id=instance.from_like.id)
        except (NodeGroup.DoesNotExist, NodeProfile.DoesNotExist) as e:
            raise ObjectDoesNotExist

        g.likes.connect(n)

@receiver(post_delete, sender=LikeGroup)
def handle_delete_like(sender, instance, *args, **kwargs):
    try:
        g = NodeGroup.nodes.get(group_id=instance.to_like.id)
        n = NodeProfile.nodes.get(user_id=instance.from_like.id)
    except (NodeGroup.DoesNotExist, NodeProfile.DoesNotExist) as e:
        raise ObjectDoesNotExist

    g.likes.disconnect(n)