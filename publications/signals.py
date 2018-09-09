import logging

import requests
from badgify.models import Award, Badge
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.urls import reverse_lazy
from embed_video.backends import detect_backend, EmbedVideoException
from requests.exceptions import MissingSchema

from notifications.signals import notify
from user_profile.node_models import NodeProfile
from .models import Publication, ExtraContent
from django.db.models import Sum, Count, When, Case, Value, IntegerField, Q

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@receiver(m2m_changed, sender=Publication.user_give_me_like.through)
def publication_received_like(sender, **kwargs):
    action = kwargs.pop('action', None)

    if action == "post_add":
        instance = kwargs.pop('instance', None)

        qs = Publication.objects.filter(author_id=instance.author_id).aggregate(
            likes=Count(Case(When(~Q(user_give_me_like=instance.author) & ~Q(user_give_me_like=None), then=Value(1)))))

        if not qs or not qs['likes']:
            return

        print(qs)
        if qs['likes'] >= 100:
            Award.objects.get_or_create(user=instance.author, badge=Badge.objects.get(slug='editor-recipe'))
        elif qs['likes'] >= 5000:
            Award.objects.get_or_create(user=instance.author, badge=Badge.objects.get(slug='pulitzer-recipe'))


@receiver(post_save, sender=Publication)
def publication_handler(sender, instance, created, **kwargs):
    # foo is following faa
    if instance.event_type == 2:
        return

    is_edited = getattr(instance, '_edited', False)

    if not created and not is_edited:
        return

    total_pubs = Publication.objects.filter(author__id=instance.author_id).count()

    if total_pubs >= 10:
        Award.objects.get_or_create(user=instance.author, badge=Badge.objects.get(slug='10-pubs-reached'))
    elif total_pubs >= 1:
        Award.objects.get_or_create(user=instance.author, badge=Badge.objects.get(slug='first-publication'))

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
            ExtraContent.objects.filter(publication=instance).exclude(url=instance.extra_content.url).delete()
        else:
            ExtraContent.objects.filter(publication=instance).delete()


def add_hashtags(instance):
    soup = BeautifulSoup(instance.content, "html5lib")
    hashtags = set([x.string for x in soup.find_all('a', {'class': 'hashtag'})])
    for tag in hashtags:
        tag = tag[1:]
        instance.tags.add(tag)


xstr = lambda s: s or ""


def add_extra_content(instance):
    if not instance.content:
        return

    soup = BeautifulSoup(instance.content, "html5lib")
    link_url = [a.get('href') for a in soup.find_all('a', {'class': 'external-link'})]
    # Si no existe nuevo enlace y tiene contenido extra, eliminamos su contenido
    if (not link_url or len(link_url) <= 0) and instance.has_extra_content():
        ExtraContent.objects.filter(publication=instance).delete()  # Borramos el extra content de esta
        instance.extra_content = None
    elif link_url and len(link_url) > 0:  # Eliminamos contenido extra para añadir el nuevo
        if instance.has_extra_content():
            extra_content = instance.extra_content
            if extra_content.url != link_url[-1]:
                ExtraContent.objects.filter(publication=instance).delete()
                instance.extra_content = None

    # Detectamos el origen de la url
    try:
        backend = detect_backend(link_url[-1])  # youtube, soundcloud...
    except (EmbedVideoException, IndexError) as e:
        backend = None

    # Si existe el backend:
    if link_url and len(link_url) > 0 and backend:
        ExtraContent.objects.create(publication=instance, video=link_url[-1])

    # Si no existe el backend
    elif link_url and len(link_url) > 0:
        url = link_url[-1]  # Get last url
        try:
            response = requests.get(url)
        except MissingSchema:
            return
        soup = BeautifulSoup(response.text, "html5lib")

        description = soup.find('meta', attrs={'name': 'og:description'}) or soup.find('meta', attrs={
            'property': 'og:description'}) or soup.find('meta', attrs={'name': 'description'})
        title = soup.find('meta', attrs={'name': 'og:title'}) or soup.find('meta', attrs={
            'property': 'og:title'}) or soup.find('meta', attrs={'name': 'title'})
        image = soup.find('meta', attrs={'name': 'og:image'}) or soup.find('meta', attrs={
            'property': 'og:image'}) or soup.find('meta', attrs={'name': 'image'})

        if description:
            description = description.get('content', None)[:256]
        if title:
            title = title.get('content', None)[:63]
        if image:
            image = image.get('content', None)

        ExtraContent.objects.create(url=url, publication=instance, description=xstr(description),
                                    title=xstr(title),
                                    image=xstr(image))


@receiver(post_delete, sender=ExtraContent)
def extra_content_handler(sender, instance, **kwargs):
    print('{} was deleted'.format(instance))


def notify_mentions(instance):
    soup = BeautifulSoup(instance.content, "html5lib")
    menciones = set([a.string[1:] for a in soup.find_all('a', {'class': 'mention'})])

    users = User.objects.only('username', 'id').filter(username__in=menciones)

    for user in users:
        if instance.author.pk != user.id:
            notify.send(instance.author, actor=instance.author.username,
                        recipient=user,
                        action_object=instance,
                        verb=u'Mención',
                        description='@{0} te ha mencionado en <a href="{1}">Ver</a>'.format(instance.author.username,
                                                                                            reverse_lazy(
                                                                                                'publications:publication_detail',
                                                                                                kwargs={
                                                                                                    'publication_id': instance.id})))


def increase_affinity(instance):
    n = NodeProfile.nodes.get(title=instance.author.username)
    m = NodeProfile.nodes.get(title=instance.board_owner.username)
    # Aumentamos la fuerza de la relacion entre los usuarios
    if n.title != m.title:
        rel = n.follow.relationship(m)
        if rel:
            rel.weight = rel.weight + 1
            rel.save()


def decrease_affinity(instance):
    n = NodeProfile.nodes.get(title=instance.author.username)
    m = NodeProfile.nodes.get(title=instance.board_owner.username)
    if n.title != m.title:
        rel = n.follow.relationship(m)
        if rel:
            rel.weight = rel.weight - 1
            rel.save()
