import json
import os
import re
import uuid

from channels.layers import get_channel_layer
from django.contrib.auth.models import User
from django.db import models
from django.template.loader import render_to_string
from embed_video.fields import EmbedVideoField

from notifications.signals import notify
from publications.models import PublicationBase
from publications.utils import validate_video
from user_groups.models import GroupTheme, UserGroups
from asgiref.sync import async_to_sync

channel_layer = get_channel_layer()


def upload_image_theme_publication(instance, filename):
    """
    Funcion para calcular la ruta
    donde se almacenaran las imagenes
    de una publicacion
    """
    ext = filename.split(".")[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    final_path = os.path.join(
        "theme_publications/images", instance.publication.author.username
    )
    return os.path.join(final_path, filename)


def upload_video_theme_publication(instance, filename):
    """
    Funcion para calcular la ruta
    donde se almacenaran las imagenes
    de una publicacion
    """
    ext = filename.split(".")[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    final_path = os.path.join(
        "theme_publications/videos", instance.publication.author.username
    )
    return os.path.join(final_path, filename)


class PublicationThemeVideo(models.Model):
    publication = models.ForeignKey(
        "PublicationTheme", related_name="videos", on_delete=models.CASCADE
    )
    video = models.FileField(
        upload_to=upload_video_theme_publication, validators=[validate_video]
    )


class PublicationThemeImage(models.Model):
    publication = models.ForeignKey(
        "PublicationTheme", related_name="images", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to=upload_image_theme_publication)


class ExtraThemeContent(models.Model):
    """
    Modelo para contenido extra/adicional de una publicacion,
    por ejemplo, informacion resumida de una URL
    """

    title = models.CharField(max_length=64, default="")
    description = models.CharField(max_length=256, default="")
    image = models.URLField(null=True, blank=True)
    url = models.URLField()
    video = EmbedVideoField(null=True, blank=True)
    publication = models.OneToOneField(
        "PublicationTheme", related_name="theme_extra_content", on_delete=models.CASCADE
    )


class PublicationTheme(PublicationBase):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    board_theme = models.ForeignKey(
        GroupTheme,
        db_index=True,
        related_name="publication_board_theme",
        on_delete=models.CASCADE,
    )
    parent = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        related_name="reply_theme",
        on_delete=models.CASCADE,
    )
    user_give_me_like = models.ManyToManyField(
        User, blank=True, related_name="likes_theme_publication"
    )
    user_give_me_hate = models.ManyToManyField(
        User, blank=True, related_name="hates_theme_publication"
    )

    class Meta:
        unique_together = ("board_theme", "id")

    class MPTTMeta:
        order_insertion_by = ["-created"]

    def __str__(self):
        return self.content

    def has_extra_content(self):
        return hasattr(self, "theme_extra_content")

    @property
    def blog_channel(self):
        return "theme-publication-%d" % self.id

    def send_notification(self, request, type="pub", is_edited=False):
        """
         Enviamos a través del socket a todos aquellos usuarios
         que esten visitando el perfil donde se publica el comentario.
        """
        self.hates = 0
        self.likes = 0

        group_owner_id = UserGroups.objects.values_list("owner_id", flat=True).get(
            id=self.board_theme.board_group_id
        )

        data = {
            "type": "pub",
            "id": self.id,
            "parent_id": self.parent_id,
            "level": self.level,
            "content": render_to_string(
                request=request,
                template_name="groups/board_theme_publications.html",
                context={
                    "publications": [self],
                    "object": self.board_theme,
                    "group_owner_id": group_owner_id,
                },
            ),
        }

        async_to_sync(channel_layer.group_send)(
            self.board_theme.theme_channel, {"type": "new_publication", "message": data}
        )

        # Notificamos al board_owner de la publicacion
        if self.author_id != group_owner_id:
            notify.send(
                self.author,
                actor=self.author.username,
                recipient=self.board_theme.owner,
                action_object=self.board_theme,
                description="@{0} ha publicado en el tema {1}. <a href='/groups/theme/{2}/'>Ver</a>".format(
                    self.author.username, self.board_theme.title, self.board_theme.slug
                ),
                verb=u"Nuevos comentarios en tema de grupo",
                level="notification_board_theme",
            )
