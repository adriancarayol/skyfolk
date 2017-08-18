import logging
from django.db.models.signals import post_save, post_delete
from .models import NodeGroup, UserGroups
from user_profile.models import NodeProfile
from neomodel import db
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from guardian.shortcuts import assign_perm

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
