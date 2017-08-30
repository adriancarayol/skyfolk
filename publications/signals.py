import logging
import re
import os
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete
from django.contrib.auth.models import User
from .models import Publication, ExtraContent
from user_profile.models import NodeProfile
from user_profile.tasks import send_to_stream
from notifications.signals import notify

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@receiver(post_save, sender=Publication, dispatch_uid='publication_save')
def publication_handler(sender, instance, created, **kwargs):
    if not instance.deleted:
        logger.info('New comment by: {} with content: {}'.format(instance.author, instance.content))
        n = NodeProfile.nodes.get(user_id=instance.author.id)
        m = NodeProfile.nodes.get(user_id=instance.board_owner.id)

        # Aumentamos la fuerza de la relacion entre los usuarios
        if n.uid != m.uid:
            rel = n.follow.relationship(m)
            if rel:
                rel.weight = rel.weight + 1
                rel.save()

        # notificamos a los mencionados
        menciones = re.findall('\\@[a-zA-Z0-9_]+', instance.content)
        menciones = set(menciones)
        for mencion in menciones:
            try:
                recipientprofile = User.objects.get(username=mencion[1:])
            except User.DoesNotExist:
                continue

            if instance.author.pk != recipientprofile.pk:
                try:
                    n = NodeProfile.nodes.get(user_id=instance.author_id)
                    m = NodeProfile.nodes.get(user_id=recipientprofile.id)
                except Exception:
                    continue

                privacity = m.is_visible(n)

                if privacity and privacity != 'all':
                    continue

            notify.send(instance.author, actor=instance.author.username,
                            recipient=recipientprofile,
                            verb=u'¡te ha mencionado!',
                            description='<a href="%s">Ver</a>' % ('/publication/' + str(instance.id)))
        # enviamos a los seguidores
        if instance.author_id == instance.board_owner_id:
            send_to_stream.delay(instance.author_id, instance.id)


    else:
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
