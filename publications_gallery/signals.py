import logging
import re
import os
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete
from django.contrib.auth.models import User
from .models import PublicationPhoto, ExtraContentPubPhoto
from user_profile.models import NodeProfile
from user_profile.tasks import send_to_stream
from notifications.signals import notify

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@receiver(post_save, sender=PublicationPhoto, dispatch_uid='photo_publication_save')
def photo_publication_handler(sender, instance, created, **kwargs):
    if created:
        logger.info('New comment by: {} with content: {}'.format(instance.p_author, instance.content))
        n = NodeProfile.nodes.get(user_id=instance.p_author.id)
        m = NodeProfile.nodes.get(user_id=instance.board_photo.owner.id)

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

            if instance.p_author.pk != recipientprofile.pk:
                try:
                    n = NodeProfile.nodes.get(user_id=instance.p_author_id)
                    m = NodeProfile.nodes.get(user_id=recipientprofile.id)
                except Exception:
                    continue

                privacity = m.is_visible(n)

                if privacity and privacity != 'all':
                    continue

            notify.send(instance.p_author, actor=instance.p_author.username,
                            recipient=recipientprofile,
                            verb=u'¡te ha mencionado!',
                            description='<a href="%s">Ver</a>' % ('/publication_pdetail/' + str(instance.id)))


    if instance.deleted:
        logger.info('Publication soft deleted, with content: {}'.format(instance.content))
        n = NodeProfile.nodes.get(user_id=instance.p_author.id)
        m = NodeProfile.nodes.get(user_id=instance.board_photo.owner.id)

        if n.uid != m.uid:
            rel = n.follow.relationship(m)
            if rel:
                rel.weight = rel.weight - 1
                rel.save()

        if instance.has_extra_content():  # Para publicaciones editadas
            ExtraContentPubPhoto.objects.filter(publication=instance.id).exclude(url=instance.extra_content.url).delete()
        else:
            ExtraContentPubPhoto.objects.filter(publication=instance.id).delete()
