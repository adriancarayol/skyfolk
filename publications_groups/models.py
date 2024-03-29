import json
import os
import uuid

from channels.layers import get_channel_layer
from django.contrib.auth.models import User
from django.db import models
from django.template.loader import render_to_string
from embed_video.fields import EmbedVideoField

from notifications.signals import notify
from publications.models import PublicationBase
from publications.utils import validate_video
from user_groups.models import UserGroups, GroupTheme
from asgiref.sync import async_to_sync

channel_layer = get_channel_layer()


def upload_image_group_publication(instance, filename):
    """
    Funcion para calcular la ruta
    donde se almacenaran las imagenes
    de una publicacion
    """
    ext = filename.split(".")[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    final_path = os.path.join(
        "group_publications/images", instance.publication.author.username
    )
    return os.path.join(final_path, filename)


def upload_video_group_publication(instance, filename):
    """
    Funcion para calcular la ruta
    donde se almacenaran las imagenes
    de una publicacion
    """
    ext = filename.split(".")[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    final_path = os.path.join(
        "group_publications/videos", instance.publication.author.username
    )
    return os.path.join(final_path, filename)


class PublicationGroupVideo(models.Model):
    publication = models.ForeignKey(
        "PublicationGroup", related_name="videos", on_delete=models.CASCADE
    )
    video = models.FileField(
        upload_to=upload_video_group_publication, validators=[validate_video]
    )


class PublicationGroupImage(models.Model):
    publication = models.ForeignKey(
        "PublicationGroup", related_name="images", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to=upload_image_group_publication)


class ExtraGroupContent(models.Model):
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
        "PublicationGroup", related_name="extra_content", on_delete=models.CASCADE
    )


class PublicationGroup(PublicationBase):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    board_group = models.ForeignKey(UserGroups, db_index=True, on_delete=models.CASCADE)
    parent = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        related_name="reply_group",
        on_delete=models.CASCADE,
    )
    user_give_me_like = models.ManyToManyField(
        User, blank=True, related_name="likes_group_publication"
    )
    user_give_me_hate = models.ManyToManyField(
        User, blank=True, related_name="hates_group_publication"
    )

    class Meta:
        unique_together = ("board_group", "id")

    class MPTTMeta:
        order_insertion_by = ["-created"]

    def __str__(self):
        return self.content

    @property
    def blog_channel(self):
        return "group-publication-%d" % self.id

    def has_extra_content(self):
        return hasattr(self, "extra_content")

    def send_notification(self, request, type="pub", is_edited=False):
        """
         Enviamos a través del socket a todos aquellos usuarios
         que esten visitando el perfil donde se publica el comentario.
        """
        self.hates = 0
        self.likes = 0

        data = {
            "type": "pub",
            "id": self.id,
            "parent_id": self.parent_id,
            "level": self.level,
            "content": render_to_string(
                request=request,
                template_name="channels/new_group_publication.html",
                context={"node": self, "group_profile": self.board_group},
            ),
        }

        # Enviamos a todos los usuarios que visitan el perfil
        async_to_sync(channel_layer.group_send)(
            self.board_group.group_channel, {"type": "new_publication", "message": data}
        )

        data["content"] = render_to_string(
            request=request,
            template_name="channels/new_group_publication_detail.html",
            context={"node": self, "group_profile": self.board_group},
        )

        # Enviamos por el socket de la publicacion
        if is_edited:
            async_to_sync(channel_layer.group_send)(
                self.blog_channel, {"type": "new_publication", "message": data}
            )

        # Enviamos al blog de la publicacion
        for id in self.get_ancestors().values_list("id", flat=True):
            async_to_sync(channel_layer.group_send)(
                "group-publication-{}".format(id),
                {"type": "new_publication", "message": data},
            )

        # Notificamos al board_owner de la publicacion
        if self.author_id != self.board_group.owner_id:
            notify.send(
                self.author,
                actor=self.author.username,
                recipient=self.board_group.owner,
                action_object=self,
                description="@{0} ha publicado en el skyline del grupo {1}. <a href='/group/publication/detail/{2}/'>Ver</a>".format(
                    self.author.username, self.board_group.name, self.id
                ),
                verb=u"Skyline de grupo",
                level="notification_board_group",
            )
