import json
import uuid
import os

from channels import Group as channel_group
from django.contrib.auth.models import User
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.db import models
from publications.models import Publication
from photologue.models import Photo
from publications.models import PublicationBase
from publications.utils import get_author_avatar
from embed_video.fields import EmbedVideoField
from publications.utils import validate_video


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
    return os.path.join('skyfolk/media/photo_publications/videos', filename)


class PublicationVideo(models.Model):
    publication = models.ForeignKey('PublicationPhoto', related_name='videos')
    video = models.FileField(upload_to=upload_video_photo_publication, validators=[validate_video])


class PublicationImage(models.Model):
    publication = models.ForeignKey('PublicationPhoto', related_name='images')
    image = models.ImageField(upload_to=upload_image_photo_publication)


class PublicationPhoto(PublicationBase):
    """
    Modelo para las publicaciones en las fotos
    """
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

    def add_hashtag(self):
        """
        Añadimos los hashtags encontrados a la
        lista de tags => atributo "tags"
        """
        hashtags = [tag.strip() for tag in self.content.split() if tag.startswith("#")]
        for tag in hashtags:
            if tag.endswith((',', '.')):
                tag = tag[:-1]
            self.tags.add(tag)

    def send_notification(self, csrf_token=None, type="pub", is_edited=False):
        """
         Enviamos a través del socket a todos aquellos usuarios
         que esten visitando el perfil donde se publica el comentario.
        """
        id_parent = None
        author_parent = None
        avatar_parent = None

        if self.parent:
            id_parent = self.parent.id
            author_parent = self.parent.p_author.username
            avatar_parent = get_author_avatar(self.parent.p_author.id)

            # extra_c = self.extra_content

            # have_extra_content = False
            # if extra_c:
            #   have_extra_content = True

        notification = {
            "id": self.id,
            "content": self.content,
            "avatar_path": get_author_avatar(authorpk=self.p_author.id),
            "p_author_id": self.p_author_id,
            "board_photo_id": self.board_photo_id,
            "photo_owner": self.board_photo.owner_id,
            "p_author_username": self.p_author.username,
            "p_author_first_name": self.p_author.first_name,
            "p_author_last_name": self.p_author.last_name,
            "created": naturaltime(self.created),
            "type": type,
            "parent": id_parent,
            "level": self.get_level(),
            'is_edited': is_edited,
            'token': csrf_token,
            # 'event_type': self.event_type,
            # 'extra_content': have_extra_content,
            'parent_author': author_parent,
            # 'images': list(self.images.all().values('image')),
            'parent_avatar': avatar_parent,
        }

        # if have_extra_content:
        #   notification['extra_content_title'] = extra_c.title
        #    notification['extra_content_description'] = extra_c.description
        #   notification['extra_content_image'] = extra_c.image
        #    notification['extra_content_url'] = extra_c.url

        # Enviamos a todos los usuarios que visitan el perfil
        channel_group(self.board_photo.group_name).send({
            "text": json.dumps(notification)
        })

    def save(self, csrf_token=None, new_comment=False, is_edited=False, *args, **kwargs):
        super(PublicationPhoto, self).save(*args, **kwargs)

        if new_comment:
            if not self.deleted:
                self.send_notification(csrf_token=csrf_token, is_edited=is_edited)  # Enviar publicacion por socket
