import logging
import re

import requests
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from embed_video.backends import detect_backend, EmbedVideoException

from notifications.signals import notify
from user_profile.node_models import NodeProfile
from .models import PublicationPhoto, ExtraContentPubPhoto

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@receiver(post_save, sender=PublicationPhoto, dispatch_uid='photo_publication_save')
def photo_publication_handler(sender, instance, created, **kwargs):
    is_edited = getattr(instance, '_edited', False)

    if not created and not is_edited:
        return

    if not instance.deleted:
        logger.info('New comment by: {} with content: {}'.format(instance.p_author, instance.content))
        # Parse extra content
        add_extra_content(instance)
        # add hashtags
        add_hashtags(instance)
        # Incrementamos afinidad entre usuarios
        increase_affinity(instance)
        # notificamos a los mencionados
        notify_mentions(instance)

    else:
        logger.info('Publication soft deleted, with content: {}'.format(instance.content))
        # Reducimos afinidad entre usuarios
        decrease_affinity(instance)

        if instance.has_extra_content():  # Para publicaciones editadas
            ExtraContentPubPhoto.objects.filter(publication=instance.id).exclude(
                url=instance.publication_photo_extra_content.url).delete()
        else:
            ExtraContentPubPhoto.objects.filter(publication=instance.id).delete()


def add_hashtags(instance):
    soup = BeautifulSoup(instance.content)
    hashtags = set([x.string for x in soup.find_all('a')])
    for tag in hashtags:
        if tag.startswith('@'):
            continue
        if tag.endswith((',', '.')):
            tag = tag[:-1]
        instance.tags.add(tag)


xstr = lambda s: s or ""


def add_extra_content(instance):

    if not instance.content:
        return

    link_url = re.findall(
        r'(?:(?:https?|ftp)://)(?:\S+(?::\S*)?@)?(?:(?!(?:10|127)(?:\.\d{1,3}){3})(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)(?:\.(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,})))(?::\d{2,5})?(?:/\S*)?',
        instance.content)

    # Si no existe nuevo enlace y tiene contenido extra, eliminamos su contenido
    if (not link_url or len(link_url) <= 0) and instance.has_extra_content():
        instance.publication_photo_extra_content.delete()  # Borramos el extra content de esta
        instance.publication_photo_extra_content = None
    elif link_url and len(link_url) > 0:  # Eliminamos contenido extra para añadir el nuevo
        if instance.has_extra_content():
            publication_photo_extra_content = instance.publication_photo_extra_content
            if publication_photo_extra_content.url != link_url[-1]:
                publication_photo_extra_content.delete()
                instance.publication_photo_extra_content = None

    try:
        backend = detect_backend(link_url[-1])  # youtube o soundcloud
    except (EmbedVideoException, IndexError) as e:
        backend = None

    if link_url and len(link_url) > 0 and backend:
        ExtraContentPubPhoto.objects.create(publication=instance, video=link_url[-1])

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

        if description:
            description = description.get('content', None)[:265]
        if title:
            title = title.get('content', None)[:63]
        if image:
            image = image.get('content', None)

        ExtraContentPubPhoto.objects.create(url=url, publication=instance, description=xstr(description),
                                            title=xstr(title),
                                            image=xstr(image))


def decrease_affinity(instance):
    n = NodeProfile.nodes.get(user_id=instance.p_author.id)
    m = NodeProfile.nodes.get(user_id=instance.board_photo.owner.id)
    if n.uid != m.uid:
        rel = n.follow.relationship(m)
        if rel:
            rel.weight = rel.weight - 1
            rel.save()


def notify_mentions(instance):
    menciones = re.findall('\\@[a-zA-Z0-9_]+', instance.content)
    menciones = set(menciones)
    for mencion in menciones:
        try:
            recipientprofile = User.objects.get(username=mencion[1:])
        except User.DoesNotExist:
            continue

        if instance.p_author.pk != recipientprofile.pk:
            notify.send(instance.p_author, actor=instance.p_author.username,
                    recipient=recipientprofile,
                    verb=u'¡<a href="/profile/{0}/">{0}</a> te ha mencionado!'.format(instance.p_author.username),
                    description='<a href="%s">Ver</a>' % ('/publication_pdetail/' + str(instance.id)))


def increase_affinity(instance):
    n = NodeProfile.nodes.get(user_id=instance.p_author.id)
    m = NodeProfile.nodes.get(user_id=instance.board_photo.owner.id)
    # Aumentamos la fuerza de la relacion entre los usuarios
    if n.uid != m.uid:
        rel = n.follow.relationship(m)
        if rel:
            rel.weight = rel.weight + 1
            rel.save()
