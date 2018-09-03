import json
import logging

from channels import Group as GroupChannel
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.http import Http404
from django.template.loader import render_to_string
from guardian.shortcuts import assign_perm

from notifications.models import Notification
from user_groups.node_models import NodeGroup
from user_profile.node_models import NodeProfile, TagProfile
from .models import UserGroups, RequestGroup, LikeGroup, GroupTheme

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@receiver(post_save, sender=UserGroups)
def handle_new_group(sender, instance, created, **kwargs):
    if created:
        NodeGroup(group_id=instance.id,
                  title=instance.name).save()
        assign_perm('view_notification', instance.owner, instance)
        assign_perm('can_publish', instance.owner, instance)
        assign_perm('change_description', instance.owner, instance)
        assign_perm('delete_publication', instance.owner, instance)
        assign_perm('delete_image', instance.owner, instance)
        assign_perm('kick_member', instance.owner, instance)
        assign_perm('ban_member', instance.owner, instance)
        assign_perm('modify_notification', instance.owner, instance)

    try:
        g = NodeGroup.nodes.get(group_id=instance.id)

        for tag in instance.tags.all():
            tag = tag.name.lower()
            interest = TagProfile.nodes.get_or_none(title=tag)
            if not interest:
                interest = TagProfile(title=tag).save()
            if interest:
                g.interest.connect(interest)
    except NodeGroup.DoesNotExist:
        logger.warning('El grupo: {} no tiene un nodo en neo4j asociado'.format(instance))


@receiver(post_delete, sender=UserGroups)
def handle_delete_group(sender, instance, *args, **kwargs):
    NodeGroup.nodes.get(group_id=instance.id).delete()


@receiver(post_delete, sender=RequestGroup)
def handle_delete_request(sender, instance, *args, **kwargs):
    Notification.objects.filter(action_object_object_id=instance.id,
                                action_object_content_type=ContentType.objects.get_for_model(instance)).delete()


@receiver(m2m_changed, sender=User.user_groups.through)
def user_group_changed_handler(sender, instance, action, **kwargs):
    if isinstance(instance, UserGroups):
        pk_set = kwargs.pop('pk_set', [])
        users = User.objects.filter(id__in=pk_set).values_list('username', flat=True)

        try:
            g = NodeGroup.nodes.get(group_id=instance.id)
        except NodeGroup.DoesNotExist:
            raise ObjectDoesNotExist

        if action == 'post_add':
            for p in users:
                try:
                    n = NodeProfile.nodes.get(title=p)
                except (NodeGroup, NodeProfile) as e:
                    raise ObjectDoesNotExist

                g.members.connect(n)

        elif action == 'post_remove':
            for p in users:
                try:
                    n = NodeProfile.nodes.get(title=p)
                except (NodeGroup, NodeProfile) as e:
                    raise Http404

                g.members.disconnect(n)


@receiver(post_save, sender=LikeGroup)
def handle_new_like(sender, instance, created, *args, **kwargs):
    if created:
        try:
            g = NodeGroup.nodes.get(group_id=instance.to_like.id)
            n = NodeProfile.nodes.get(title=instance.from_like.username)
        except (NodeGroup.DoesNotExist, NodeProfile.DoesNotExist) as e:
            raise ObjectDoesNotExist

        g.likes.connect(n)


@receiver(post_delete, sender=LikeGroup)
def handle_delete_like(sender, instance, *args, **kwargs):
    try:
        g = NodeGroup.nodes.get(group_id=instance.to_like.id)
        n = NodeProfile.nodes.get(title=instance.from_like.username)
        g.likes.disconnect(n)
    except (NodeGroup.DoesNotExist, NodeProfile.DoesNotExist) as e:
        pass



@receiver(post_save, sender=GroupTheme)
def handle_new_theme(sender, instance, created, *args, **kwargs):
    if created:
        theme = render_to_string('groups/group_themes.html', {'themes': [instance, ]})
        group = UserGroups.objects.get(id=instance.board_group_id)
        data = {
            'theme': theme,
            'type': 'theme',
            'id': instance.id
        }
        GroupChannel(group.group_channel).send({
            "text": json.dumps(data)
        })
