import json
import os
import re
import uuid

from channels import Group as channel_group
from django.contrib.auth.models import User
from django.db import models
from django.template.loader import render_to_string
from embed_video.fields import EmbedVideoField

from notifications.signals import notify
from publications.models import PublicationBase
from publications.utils import validate_video
from user_groups.models import GroupTheme, UserGroups


def upload_image_theme_publication(instance, filename):
    """
    Funcion para calcular la ruta
    donde se almacenaran las imagenes
    de una publicacion
    """
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('theme_publications/images', filename)


def upload_video_theme_publication(instance, filename):
    """
    Funcion para calcular la ruta
    donde se almacenaran las imagenes
    de una publicacion
    """
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('theme_publications/videos', filename)


class PublicationThemeVideo(models.Model):
    publication = models.ForeignKey('PublicationTheme', related_name='videos', on_delete=models.CASCADE)
    video = models.FileField(upload_to=upload_video_theme_publication, validators=[validate_video])


class PublicationThemeImage(models.Model):
    publication = models.ForeignKey('PublicationTheme', related_name='images', on_delete=models.CASCADE)
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
    publication = models.OneToOneField('PublicationTheme', related_name='theme_extra_content', on_delete=models.CASCADE)


class PublicationTheme(PublicationBase):
    author = models.ForeignKey(User)
    board_theme = models.ForeignKey(GroupTheme, db_index=True, related_name='publication_board_theme',
                                    on_delete=models.CASCADE)
    parent = models.ForeignKey('self', blank=True, null=True,
                               related_name='reply_theme')
    user_give_me_like = models.ManyToManyField(User, blank=True,
                                               related_name='likes_theme_publication')
    user_give_me_hate = models.ManyToManyField(User, blank=True,
                                               related_name='hates_theme_publication')

    class Meta:
        unique_together = ('board_theme', 'id')

    class MPTTMeta:
        order_insertion_by = ['-created']

    def __str__(self):
        return self.content

    def has_extra_content(self):
        return hasattr(self, 'theme_extra_content')

    @property
    def blog_channel(self):
        return "theme-publication-%d" % self.id

    def send_notification(self, request, type="pub", is_edited=False):
        """
         Enviamos a través del socket a todos aquellos usuarios
         que esten visitando el perfil donde se publica el comentario.
        """

        group_owner_id = UserGroups.objects.values_list('owner_id', flat=True).get(
            id=self.board_theme.board_group_id)

        data = {
            'type': 'pub',
            'id': self.id,
            'parent_id': self.parent_id,
            'level': self.level,
            'content': render_to_string(request=request, template_name='groups/board_theme_publications.html',
                                        context={'publications': [self, ], 'object': self.board_theme, 'group_owner_id': group_owner_id})
        }

        # Enviamos a todos los usuarios que visitan el perfil
        channel_group(self.board_theme.theme_channel).send({
            "text": json.dumps(data)
        })

        # Notificamos al board_owner de la publicacion
        notify.send(self.author, actor=self.author.username,
                    recipient=self.board_theme.owner,
                    description="Te avisamos de que @{0} ha publicado en el tema {1}.".format(
                        self.author.username, self.board_theme.title),
                    verb=u'<a href="/profile/{0}">@{0}</a> ha publicado en el tema {1}.'.format(self.author.username,
                                                                                                self.board_theme.title),
                    level='notification_board_theme')