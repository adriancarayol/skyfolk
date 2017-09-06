import logging
import re

import requests
from badgify.models import Award, Badge
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from embed_video.backends import detect_backend, EmbedVideoException

from notifications.signals import notify
from user_profile.models import NodeProfile
from user_profile.tasks import send_to_stream
from .models import Publication, ExtraContent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@receiver(post_save, sender=Publication, dispatch_uid='publication_save')
def publication_handler(sender, instance, created, **kwargs):
    if created:
        total_pubs = Publication.objects.filter(author__id=instance.author_id).count()
        if total_pubs == 10:
            Award.objects.create(user=instance.author, badge=Badge.objects.get(slug='10-pubs-reached'))

    if not instance.deleted:
        logger.info('New comment by: {} with content: {}'.format(instance.author, instance.content))

        # Parse extra content
        add_extra_content(instance)
        # Add hashtags
        add_hashtags(instance)
        # Incrementamos afinidad entre usuarios
        increase_affinity(instance)
        # notificamos a los mencionados
        notify_mentions(instance)

    else:
        logger.info('Publication soft deleted, with content: {}'.format(instance.content))
        decrease_affinity(instance)

        if instance.has_extra_content():  # Para publicaciones editadas
            ExtraContent.objects.filter(publication=instance.id).exclude(url=instance.extra_content.url).delete()
        else:
            ExtraContent.objects.filter(publication=instance.id).delete()


def add_hashtags(instance):
    hashtags = [tag.strip() for tag in instance.content.split() if tag.startswith("#")]
    hashtags = set(hashtags)
    for tag in hashtags:
        if tag.endswith((',', '.')):
            tag = tag[:-1]
            instance.tags.add(tag)


def add_extra_content(instance):
    link_url = re.findall(
        r'(?:(?:https?|ftp)://)(?:\S+(?::\S*)?@)?(?:(?!(?:10|127)(?:\.\d{1,3}){3})(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)(?:\.(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,})))(?::\d{2,5})?(?:/\S*)?',
        instance.content)

    # Si no existe nuevo enlace y tiene contenido extra, eliminamos su contenido
    if not link_url and len(link_url) <= 0 and instance.has_extra_content():
        instance.extra_content.delete()  # Borramos el extra content de esta
        return
    elif link_url and len(link_url) > 0:  # Eliminamos contenido extra para añadir el nuevo
        if instance.has_extra_content():
            extra_content = instance.extra_content
            if extra_content.url != link_url[-1]:
                extra_content.delete()

    # Detectamos el origen de la url
    try:
        backend = detect_backend(link_url[-1])  # youtube, soundcloud...
    except (EmbedVideoException, IndexError) as e:
        backend = None

    # Si existe el backend:
    if link_url and len(link_url) > 0 and backend:
        ExtraContent.objects.get_or_create(publication=instance, video=link_url[-1])

    # Si no existe el backend
    elif link_url and len(link_url) > 0:
        url = link_url[-1]  # Get last url
        response = requests.get(url)
        soup = BeautifulSoup(response.text)

        description = soup.find('meta', attrs={'name': 'og:description'}) or soup.find('meta', attrs={
            'property': 'og:description'}) or soup.find('meta', attrs={'name': 'description'})
        title = soup.find('meta', attrs={'name': 'og:title'}) or soup.find('meta', attrs={
            'property': 'og:title'}) or soup.find('meta', attrs={'name': 'title'})
        image = soup.find('meta', attrs={'name': 'og:image'}) or soup.find('meta', attrs={
            'property': 'og:image'}) or soup.find('meta', attrs={'name': 'image'})

        extra_c, created = ExtraContent.objects.get_or_create(url=url, publication=instance)

        if description:
            extra_c.description = description.get('content', None)[:265]
        if title:
            extra_c.title = title.get('content', None)[:63]
        if image:
            extra_c.image = image.get('content', None)
        extra_c.save()


def notify_mentions(instance):
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
        send_to_stream.apply_async(args=[instance.author_id, instance.id], queue='low')


def increase_affinity(instance):
    n = NodeProfile.nodes.get(user_id=instance.author.id)
    m = NodeProfile.nodes.get(user_id=instance.board_owner.id)
    # Aumentamos la fuerza de la relacion entre los usuarios
    if n.uid != m.uid:
        rel = n.follow.relationship(m)
        if rel:
            rel.weight = rel.weight + 1
            rel.save()


def decrease_affinity(instance):
    n = NodeProfile.nodes.get(user_id=instance.author.id)
    m = NodeProfile.nodes.get(user_id=instance.board_owner.id)
    if n.uid != m.uid:
        rel = n.follow.relationship(m)
        if rel:
            rel.weight = rel.weight - 1
            rel.save()
