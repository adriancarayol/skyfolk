import logging
from django.db.models.signals import post_save, post_delete
from .models import NodeGroup, UserGroups
from user_profile.models import NodeProfile
from neomodel import db
from django.dispatch import receiver
from django.template.defaultfilters import slugify

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

"""
@receiver(post_save, sender=UserGroups)
def handle_new_group(sender, instance, created, **kwargs):
    if created:  # Primera vez que se crea el usuario, creamos Perfil y Nodo
        try:
            with db.transaction:
                g = NodeGroup(group_id=instance.id, title=instance.name,
                            slug=slugify(instance.name)).save()
                print('Group created')
                g.owner.connect(NodeProfile.nodes.get(user_id=instance.owner_id))
            logger.info("POST_SAVE : Create NodeGroup, Group: %s" % instance)
        except Exception as e:
            logger.info(
               "POST_SAVE : No se pudo crear la instancia NodeGroup para el grupo : %s" % instance)
"""
