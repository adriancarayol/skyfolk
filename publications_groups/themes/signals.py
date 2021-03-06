import re
import requests
import logging
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse_lazy
from embed_video.backends import detect_backend, EmbedVideoException
from requests import RequestException
from requests.exceptions import MissingSchema
from user_profile.models import RelationShipProfile, Request
from user_profile.constants import FOLLOWING
from notifications.signals import notify
from publications_groups.themes.models import PublicationTheme, ExtraThemeContent


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@receiver(post_save, sender=PublicationTheme, dispatch_uid="publication_theme_save")
def theme_publication_handler(sender, instance, created, **kwargs):
    is_edited = getattr(instance, "_edited", False)

    if not created and not is_edited:
        return

    if not instance.deleted:
        logger.info(
            "New comment by: {} with content: {}".format(
                instance.author, instance.content
            )
        )

        # Parse extra content
        add_extra_content(instance)
        # add hashtag
        add_hashtags(instance)
        # Incrementamos afinidad entre usuarios
        increase_affinity(instance)
        # notificamos a los mencionados
        notify_mentions(instance)

    else:
        logger.info(
            "Publication soft deleted, with content: {}".format(instance.content)
        )
        decrease_affinity(instance)

        if instance.has_extra_content():  # Para publicaciones editadas
            ExtraThemeContent.objects.filter(publication=instance.id).exclude(
                url=instance.extra_content.url
            ).delete()
        else:
            ExtraThemeContent.objects.filter(publication=instance.id).delete()


def add_hashtags(instance):
    soup = BeautifulSoup(instance.content, "html5lib")
    hashtags = set([x.string for x in soup.find_all("a", {"class": "hashtag"})])
    for tag in hashtags:
        tag = tag[1:]
        instance.tags.add(tag)


xstr = lambda s: s or ""


def add_extra_content(instance):
    if not instance.content:
        return

    soup = BeautifulSoup(instance.content, "html5lib")
    link_url = [a.get("href") for a in soup.find_all("a", {"class": "external-link"})]

    # Si no existe nuevo enlace y tiene contenido extra, eliminamos su contenido
    if (not link_url or len(link_url) <= 0) and instance.has_extra_content():
        instance.theme_extra_content.delete()  # Borramos el extra content de esta
        instance.theme_extra_content = None
    elif (
        link_url and len(link_url) > 0
    ):  # Eliminamos contenido extra para añadir el nuevo
        if instance.has_extra_content():
            theme_extra_content = instance.theme_extra_content
            if theme_extra_content.url != link_url[-1]:
                theme_extra_content.delete()
                instance.theme_extra_content = None
    # Detectamos el origen de la url
    try:
        backend = detect_backend(link_url[-1])  # youtube, soundcloud...
    except (EmbedVideoException, IndexError) as e:
        backend = None
    # Si existe el backend:
    if link_url and len(link_url) > 0 and backend:
        ExtraThemeContent.objects.create(publication=instance, video=link_url[-1])
    # Si no existe el backend
    elif link_url and len(link_url) > 0:
        url = link_url[-1]  # Get last url
        try:
            response = requests.get(url)
        except RequestException as e:
            logger.error(e)
            return
        soup = BeautifulSoup(response.text, "html5lib")
        description = (
            soup.find("meta", attrs={"name": "og:description"})
            or soup.find("meta", attrs={"property": "og:description"})
            or soup.find("meta", attrs={"name": "description"})
        )
        title = (
            soup.find("meta", attrs={"name": "og:title"})
            or soup.find("meta", attrs={"property": "og:title"})
            or soup.find("meta", attrs={"name": "title"})
        )
        image = (
            soup.find("meta", attrs={"name": "og:image"})
            or soup.find("meta", attrs={"property": "og:image"})
            or soup.find("meta", attrs={"name": "image"})
        )

        if description:
            description = description.get("content", None)[:256]
        if title:
            title = title.get("content", None)[:63]
        if image:
            image = image.get("content", None)

        ExtraThemeContent.objects.create(
            url=url,
            publication=instance,
            description=xstr(description),
            title=xstr(title),
            image=xstr(image),
        )


def notify_mentions(instance):
    soup = BeautifulSoup(instance.content, "html5lib")
    menciones = set([a.string[1:] for a in soup.find_all("a", {"class": "mention"})])

    users = User.objects.only("username", "id").filter(username__in=menciones)

    for user in users:
        if instance.author.id != user.id:
            notify.send(
                instance.author,
                actor=instance.author.username,
                recipient=user,
                action_object=instance.board_theme,
                verb=u"Mención",
                description='@{0} te ha mencionado en <a href="{1}">Ver</a>'.format(
                    instance.author.username,
                    reverse_lazy(
                        "user_groups:group_theme",
                        kwargs={"slug": instance.board_theme.slug},
                    ),
                ),
            )


def increase_affinity(instance):
    try:
        relation = RelationShipProfile.objects.get(
            from_profile=instance.author.profile,
            to_profile=instance.board_theme.owner.profile,
            type=FOLLOWING,
        )
        relation.weight = relation.weight + 1
    except RelationShipProfile.DoesNotExist:
        pass


def decrease_affinity(instance):
    try:
        relation = RelationShipProfile.objects.get(
            from_profile=instance.author.profile,
            to_profile=instance.board_theme.owner.profile,
            type=FOLLOWING,
        )
        relation.weight = relation.weight - 1
    except RelationShipProfile.DoesNotExist:
        pass
