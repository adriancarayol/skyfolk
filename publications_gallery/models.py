import json
import os
import re
import uuid

import bleach
from channels import Group as channel_group
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from embed_video.fields import EmbedVideoField

from photologue.models import Photo
from publications.models import Publication
from publications.models import PublicationBase
from publications.utils import validate_video

# Los tags HTML que permitimos en los comentarios
ALLOWED_TAGS = bleach.ALLOWED_TAGS + settings.ALLOWED_TAGS
ALLOWED_STYLES = bleach.ALLOWED_STYLES + settings.ALLOWED_STYLES
ALLOWED_ATTRIBUTES = dict(bleach.ALLOWED_ATTRIBUTES)
ALLOWED_ATTRIBUTES.update(settings.ALLOWED_ATTRIBUTES)


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
    publication = models.OneToOneField('PublicationPhoto', related_name='publication_photo_extra_content')


def upload_image_photo_publication(instance, filename):
    """
    Funcion para calcular la ruta
    donde se almacenaran las imagenes
    de una publicacion
    """
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('photo_publications/images', filename)


def upload_video_photo_publication(instance, filename):
    """
    Funcion para calcular la ruta
    donde se almacenaran las imagenes
    de una publicacion
    """
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('photo_publications/videos', filename)


class PublicationPhotoVideo(models.Model):
    publication = models.ForeignKey('PublicationPhoto', related_name='videos')
    video = models.FileField(upload_to=upload_video_photo_publication, validators=[validate_video])


class PublicationPhotoImage(models.Model):
    publication = models.ForeignKey('PublicationPhoto', related_name='images')
    image = models.ImageField(upload_to=upload_image_photo_publication)


class PublicationPhoto(PublicationBase):
    """
    Modelo para las publicaciones en las fotos
    """
    EVENT_CHOICES = (
        (1, _("publication")),
        (3, _("link")),
        (4, _("relevant")),
    )

    p_author = models.ForeignKey(User, null=True)
    board_photo = models.ForeignKey(Photo, related_name='board_photo')
    user_give_me_like = models.ManyToManyField(User, blank=True,
                                               related_name='likes_photo_me')
    user_give_me_hate = models.ManyToManyField(User, blank=True,
                                               related_name='hate_photo_me')
    user_share_me = models.ManyToManyField(User, blank=True,
                                           related_name='share_photo_me')
    parent = models.ForeignKey('self', blank=True, null=True,
                               related_name='reply_photo')
    event_type = models.PositiveIntegerField(choices=EVENT_CHOICES, default=1, blank=True)

    class MPTTMeta:
        order_insertion_by = ['-created']

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
        return Publication.objects.filter(shared_photo_publication_id=self.id, author_id=self.p_author_id,
                                          deleted=False).count()

    @property
    def get_channel_name(self):
        return "photo-pub-%s" % self.id

    def has_extra_content(self):
        return hasattr(self, 'publication_photo_extra_content')

    def parse_extra_content(self):
        # Buscamos en el contenido del mensaje una URL y mostramos un breve resumen de ella
        link_url = re.findall(
            r'(?:(?:https?|ftp)://)(?:\S+(?::\S*)?@)?(?:(?!(?:10|127)(?:\.\d{1,3}){3})(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)(?:\.(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,})))(?::\d{2,5})?(?:/\S*)?',
            self.content)
        if link_url and len(link_url) > 0:
            self.event_type = 3

    def send_notification(self, request, type="pub", is_edited=False):
        """
         Enviamos a través del socket a todos aquellos usuarios
         que esten visitando el perfil donde se publica el comentario.
        """
        data = {
            'type': type,
            'id': self.id,
            'parent_id': self.parent_id,
            'level': self.level,
            'content': render_to_string(request=request,
                                        template_name='channels/new_photo_publication.html',
                                        context={'node': self, 'photo': self.board_photo})
        }

        # Enviamos a todos los usuarios que visitan la foto
        channel_group(self.board_photo.group_name).send({
            "text": json.dumps(data)
        })

        data['content'] = render_to_string(request=request, template_name='channels/new_photo_publication_detail.html',
                                           context={'node': self, 'photo': self.board_photo})

        if is_edited:
            channel_group(self.get_channel_name).send({
                'text': json.dumps(data)
            })
        # Enviamos al blog de la publicacion
        [channel_group(x.get_channel_name).send({
            "text": json.dumps(data)
        }) for x in self.get_ancestors().only('id')]
