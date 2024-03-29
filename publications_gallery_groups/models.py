import json
import os
import uuid

import bleach
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.template.loader import render_to_string
from embed_video.fields import EmbedVideoField
from channels.layers import get_channel_layer
from notifications.signals import notify
from photologue_groups.models import PhotoGroup, VideoGroup
from publications.models import Publication
from publications.models import PublicationBase
from publications.utils import validate_video
from asgiref.sync import async_to_sync

# Los tags HTML que permitimos en los comentarios
ALLOWED_TAGS = bleach.ALLOWED_TAGS + settings.ALLOWED_TAGS
ALLOWED_STYLES = bleach.ALLOWED_STYLES + settings.ALLOWED_STYLES
ALLOWED_ATTRIBUTES = dict(bleach.ALLOWED_ATTRIBUTES)
ALLOWED_ATTRIBUTES.update(settings.ALLOWED_ATTRIBUTES)

channel_layer = get_channel_layer()


class ExtraContentPubPhoto(models.Model):
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
        "PublicationGroupMediaPhoto",
        related_name="publication_group_multimedia_photo_extra_content",
        on_delete=models.CASCADE,
    )


def upload_image_photo_publication(instance, filename):
    """
    Funcion para calcular la ruta
    donde se almacenaran las imagenes
    de una publicacion
    """
    ext = filename.split(".")[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    final_path = os.path.join(
        "photo_publications/groups/images", instance.publication.author.username
    )
    return os.path.join(final_path, filename)


def upload_video_photo_publication(instance, filename):
    """
    Funcion para calcular la ruta
    donde se almacenaran las imagenes
    de una publicacion
    """
    ext = filename.split(".")[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    final_path = os.path.join(
        "photo_publications/groups/videos", instance.publication.author.username
    )
    return os.path.join(final_path, filename)


class PublicationPhotoVideo(models.Model):
    publication = models.ForeignKey(
        "PublicationGroupMediaPhoto", related_name="videos", on_delete=models.CASCADE
    )
    video = models.FileField(
        upload_to=upload_video_photo_publication, validators=[validate_video]
    )


class PublicationPhotoImage(models.Model):
    publication = models.ForeignKey(
        "PublicationGroupMediaPhoto", related_name="images", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to=upload_image_photo_publication)


class PublicationGroupMediaPhoto(PublicationBase):
    """
    Modelo para las publicaciones en las fotos
    """

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    board_photo = models.ForeignKey(
        PhotoGroup,
        related_name="board_group_multimedia_photo",
        on_delete=models.CASCADE,
    )
    user_give_me_like = models.ManyToManyField(
        User, blank=True, related_name="likes_group_multimedia_photo_me"
    )
    user_give_me_hate = models.ManyToManyField(
        User, blank=True, related_name="hate_group_multimedia_photo_me"
    )
    parent = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        related_name="group_multimedia_reply_photo",
        on_delete=models.CASCADE,
    )

    class MPTTMeta:
        order_insertion_by = ["-created"]

    def __str__(self):
        return self.content

    @property
    def total_likes(self):
        return self.user_give_me_like.count()

    @property
    def total_hates(self):
        return self.user_give_me_hate.count()

    @property
    def get_channel_name(self):
        return "group-photo-pub-%s" % self.id

    def has_extra_content(self):
        return hasattr(self, "publication_group_multimedia_photo_extra_content")

    def send_notification(self, request, type="pub", is_edited=False):
        """
         Enviamos a través del socket a todos aquellos usuarios
         que esten visitando el perfil donde se publica el comentario.
        """
        self.hates = 0
        self.likes = 0

        data = {
            "type": type,
            "id": self.id,
            "parent_id": self.parent_id,
            "level": self.level,
            "content": render_to_string(
                request=request,
                template_name="channels/new_group_gallery_publication.html",
                context={"node": self, "object": self.board_photo},
            ),
        }

        # Enviamos a todos los usuarios que visitan la foto
        async_to_sync(channel_layer.group_send)(
            self.board_photo.group_name, {"type": "new_publication", "message": data}
        )

        data["content"] = render_to_string(
            request=request,
            template_name="channels/new_photo_group_publication_detail.html",
            context={"node": self, "object": self.board_photo},
        )

        if is_edited:
            async_to_sync(channel_layer.group_send)(
                self.get_channel_name, {"type": "new_publication", "message": data}
            )

        # Enviamos al blog de la publicacion
        for publication in self.get_ancestors().only("id"):
            async_to_sync(channel_layer.group_send)(
                publication.get_channel_name,
                {"type": "new_publication", "message": data},
            )

        # Enviamos al owner de la notificacion
        if self.author_id != self.board_photo.owner_id:
            notify.send(
                self.author,
                actor=self.author.username,
                recipient=self.board_photo.owner,
                action_object=self,
                description="@{0} ha publicado en una foto. <a href='/group/multimedia/publication/detail/{1}/'>Ver</a>".format(
                    self.author.username, self.id
                ),
                verb=u"Nuevos comentarios en imagen",
                level="notification_board_owner",
            )


# Video publications


class ExtraContentPubVideo(models.Model):
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
        "PublicationGroupMediaVideo",
        related_name="publication_group_multimedia_video_extra_content",
        on_delete=models.CASCADE,
    )


def upload_image_video_publication(instance, filename):
    """
    Funcion para calcular la ruta
    donde se almacenaran las imagenes
    de una publicacion
    """
    ext = filename.split(".")[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join("video_publications/groups/images", filename)


def upload_video_video_publication(instance, filename):
    """
    Funcion para calcular la ruta
    donde se almacenaran las imagenes
    de una publicacion
    """
    ext = filename.split(".")[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join("video_publications/groups/videos", filename)


class PublicationVideoVideo(models.Model):
    publication = models.ForeignKey(
        "PublicationGroupMediaVideo", related_name="videos", on_delete=models.CASCADE
    )
    video = models.FileField(
        upload_to=upload_video_photo_publication, validators=[validate_video]
    )


class PublicationVideoImage(models.Model):
    publication = models.ForeignKey(
        "PublicationGroupMediaVideo", related_name="images", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to=upload_image_photo_publication)


class PublicationGroupMediaVideo(PublicationBase):
    """
    Modelo para las publicaciones en las fotos
    """

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    board_video = models.ForeignKey(
        VideoGroup,
        related_name="board_group_multimedia_video",
        on_delete=models.CASCADE,
    )
    user_give_me_like = models.ManyToManyField(
        User, blank=True, related_name="likes_group_multimedia_video_me"
    )
    user_give_me_hate = models.ManyToManyField(
        User, blank=True, related_name="hate_group_multimedia_video_me"
    )
    parent = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        related_name="roup_multimedia_reply_photo",
        on_delete=models.CASCADE,
    )

    class MPTTMeta:
        order_insertion_by = ["-created"]

    def __str__(self):
        return self.content

    def has_extra_content(self):
        return hasattr(self, "publication_group_multimedia_video_extra_content")

    @property
    def total_likes(self):
        return self.user_give_me_like.count()

    @property
    def total_hates(self):
        return self.user_give_me_hate.count()

    @property
    def get_channel_name(self):
        return "group-video-pub-%s" % self.id

    def send_notification(self, request, type="pub", is_edited=False):
        """
         Enviamos a través del socket a todos aquellos usuarios
         que esten visitando el perfil donde se publica el comentario.
        """
        self.hates = 0
        self.likes = 0

        data = {
            "type": type,
            "id": self.id,
            "parent_id": self.parent_id,
            "level": self.level,
            "content": render_to_string(
                request=request,
                template_name="channels/new_video_group_publication.html",
                context={"node": self, "object": self.board_video},
            ),
        }

        # Enviamos a todos los usuarios que visitan la foto
        async_to_sync(channel_layer.group_send)(
            self.board_video.group_name, {"type": "new_publication", "message": data}
        )

        data["content"] = render_to_string(
            request=request,
            template_name="channels/new_video_group_publication_detail.html",
            context={"node": self, "object": self.board_video},
        )

        if is_edited:
            async_to_sync(channel_layer.group_send)(
                self.get_channel_name, {"type": "new_publication", "message": data}
            )

        # Enviamos al blog de la publicacion
        for publication in self.get_ancestors().defer():
            async_to_sync(channel_layer.group_send)(
                publication.get_channel_name,
                {"type": "new_publication", "message": data},
            )

        # Enviamos al owner de la notificacion
        if self.author_id != self.board_video.owner_id:
            notify.send(
                self.author,
                actor=self.author.username,
                recipient=self.board_video.owner,
                action_object=self,
                description="@{0} ha publicado en un vídeo. <a href='/group/multimedia/video/publication/detail/{1}/'>Ver</a>".format(
                    self.author.username, self.id
                ),
                verb=u"Nuevos comentarios en vídeo",
                level="notification_board_owner",
            )
