import re
import uuid

import bleach
from asgiref.sync import async_to_sync
from bleach.linkifier import Linker
from channels.layers import get_channel_layer
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from embed_video.fields import EmbedVideoField
from mptt.models import MPTTModel, TreeForeignKey
from taggit.managers import TaggableManager

from notifications.signals import notify
from photologue.models import Photo
from publications.utils import validate_video, set_link_class
from user_profile.utils import group_name
from .managers import PublicationManager
from .utils import get_channel_name

# Los tags HTML que permitimos en los comentarios
ALLOWED_TAGS = bleach.ALLOWED_TAGS + settings.ALLOWED_TAGS
ALLOWED_STYLES = bleach.ALLOWED_STYLES + settings.ALLOWED_STYLES
ALLOWED_ATTRIBUTES = dict(bleach.ALLOWED_ATTRIBUTES)
ALLOWED_ATTRIBUTES.update(settings.ALLOWED_ATTRIBUTES)

channel_layer = get_channel_layer()


def upload_image_publication(instance, filename):
    """
    Funcion para calcular la ruta
    donde se almacenaran las imagenes
    de una publicacion
    """
    ext = filename.split(".")[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return "{0}/{1}/{2}".format(
        "publications/images", instance.publication.author.username, filename
    )


def upload_video_publication(instance, filename):
    """
    Funcion para calcular la ruta
    donde se almacenaran las imagenes
    de una publicacion
    """
    ext = filename.split(".")[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return "{0}/{1}/{2}".format(
        "publications/videos", instance.publication.author.username, filename
    )


class PublicationBase(MPTTModel):
    EVENT_CHOICES = (
        (1, _("publication")),
        (2, _("new_relation")),
        (3, _("link")),
        (4, _("relevant")),
        (5, _("image")),
        (6, _("shared")),
    )

    content = models.TextField(max_length=10000)
    created = models.DateTimeField(auto_now_add=True)
    edition_date = models.DateTimeField(null=True, blank=True)
    tags = TaggableManager(blank=True)
    deleted = models.BooleanField(default=False, blank=True)
    event_type = models.IntegerField(choices=EVENT_CHOICES, default=1)

    class Meta:
        abstract = True

    def get_content_type(self):
        """:return: Content type for this instance."""
        return ContentType.objects.get_for_model(self)

    def get_content_type_id(self):
        """:return: Content type ID for this instance"""
        return self.get_content_type().pk

    def get_children_count(self):
        """
        Util para contar cuantos nodos hijos inmediatos tiene la raiz (el comentario raiz)
        :return: El numero de nodos hijo
        """
        # return self.get_descendants().filter(level__lte=1, deleted=False).count()
        return self.get_descendants().filter(deleted=False).count()

    def get_descendants_not_deleted(self):
        return self.get_descendants().filter(deleted=False).count()

    def add_hashtag(self):
        hashtags = set(
            [tag.strip() for tag in self.content.split() if tag.startswith("#")]
        )

        for tag in hashtags:
            if tag.endswith((",", ".")):
                tag = tag[:-1]
            self.content = self.content.replace(
                tag,
                '<a class="hashtag" href="/user-search/?q={0}">{1}</a>'.format(
                    tag[1:], tag
                ),
            )

    def parse_mentions(self):
        """
        Buscamos menciones en el contenido del mensaje
        y enviamos un mensaje al usuario
        """
        menciones = re.findall("\\@[a-zA-Z0-9_]+", self.content)
        menciones = set([x[1:] for x in menciones])

        users = User.objects.values_list("username", flat=True).filter(
            username__in=menciones
        )

        for user in users:
            self.content = self.content.replace(
                "@" + user,
                '<a class="mention" href="/profile/{0}/">@{0}</a>'.format(user),
            )

    def parse_content(self):
        """
        Parseamos el contenido en busca de
        tags html no permitidos y los eliminamos
        """
        self.content = re.sub(r'\n\n+', '\n\n', self.content)
        self.content = re.sub(r'\r\r+', '\r\r', self.content)
        self.content = ''.join(self.content.strip())
        """
        self.content = bleach.clean(self.content, tags=ALLOWED_TAGS,
                                    attributes=ALLOWED_ATTRIBUTES, styles=ALLOWED_STYLES)
        """
        linker = Linker(callbacks=[set_link_class])
        self.content = bleach.clean(self.content, tags=[""])
        self.content = linker.linkify(self.content)


class ExtraContent(models.Model):
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
        "Publication", related_name="extra_content", on_delete=models.CASCADE
    )


class Publication(PublicationBase):
    """
    Modelo para las publicaciones de usuario (en perfiles de usuarios)
    """

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    board_owner = models.ForeignKey(
        User, related_name="board_owner", db_index=True, on_delete=models.CASCADE
    )
    user_give_me_like = models.ManyToManyField(
        User, blank=True, related_name="likes_me"
    )
    user_give_me_hate = models.ManyToManyField(
        User, blank=True, related_name="hates_me"
    )
    shared_publication = models.ForeignKey(
        "self", blank=True, null=True, on_delete=models.CASCADE
    )
    shared_group_publication = models.ForeignKey(
        "publications_groups.PublicationGroup",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    parent = TreeForeignKey(
        "self",
        blank=True,
        null=True,
        related_name="reply",
        db_index=True,
        on_delete=models.CASCADE,
    )
    objects = PublicationManager()

    class Meta:
        unique_together = (
            ("shared_publication", "author"),
            ("shared_group_publication", "author"),
            ("board_owner", "id"),
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
    def total_shares(self):
        return Publication.objects.filter(
            shared_publication_id=self.id, deleted=False
        ).count()

    def has_extra_content(self):
        return hasattr(self, "extra_content")

    def send_notification(self, request, is_edited=False):
        self.hates = 0
        self.likes = 0

        data = {
            "type": "pub",
            "id": self.id,
            "parent_id": self.parent_id,
            "level": self.level,
            "is_edited": is_edited,
            "content": render_to_string(
                request=request,
                template_name="channels/new_publication.html",
                context={"node": self, "user_profile": self.board_owner},
            ),
        }

        # Enviamos a todos los usuarios que visitan el perfil

        async_to_sync(channel_layer.group_send)(
            group_name(self.board_owner_id),
            {"type": "new_publication", "message": data},
        )

        # TODO: Mezclar templates para ahorrar el render
        data["content"] = render_to_string(
            request=request,
            template_name="channels/new_publication_detail.html",
            context={"node": self, "user_profile": self.board_owner},
        )

        # Enviamos por el socket de la publicacion
        if is_edited:
            async_to_sync(channel_layer.group_send)(
                get_channel_name(self.id), {"type": "new_publication", "message": data}
            )

        # Enviamos al blog de la publicacion
        for id in self.get_ancestors().values_list("id", flat=True):
            async_to_sync(channel_layer.group_send)(
                get_channel_name(id), {"type": "new_publication", "message": data}
            )

        # Notificamos al board_owner de la publicacion
        if self.author_id != self.board_owner_id:
            notify.send(
                self.author,
                actor=self.author.username,
                recipient=self.board_owner,
                action_object=self,
                description="@{0} ha publicado en tu skyline. <a href='/publication/{1}/'>Ver</a>".format(
                    self.author.username, self.id
                ),
                verb=u"Skyline",
                level="notification_board_owner",
            )


class PublicationVideo(models.Model):
    publication = models.ForeignKey(
        Publication, related_name="videos", on_delete=models.CASCADE
    )
    video = models.FileField(
        upload_to=upload_video_publication, validators=[validate_video]
    )


class PublicationImage(models.Model):
    publication = models.ForeignKey(
        Publication, related_name="images", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to=upload_image_publication)


class PublicationDeleted(models.Model):
    """
    Contiene las publicaciones eliminadas por los usuarios
    """

    TYPE_PUBLICATIONS = ((1, _("skyline")), (2, _("photo")))
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=False, null=True, max_length=500)
    created = models.DateTimeField(null=True)
    type_publication = models.IntegerField(choices=TYPE_PUBLICATIONS, default=1)
