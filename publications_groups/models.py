import re
import uuid
import os
import json
from django.contrib.auth.models import User
from django.db import models
from channels import Group as channel_group
from embed_video.fields import EmbedVideoField
from user_profile.tasks import send_email
from publications.models import PublicationBase
from user_groups.models import UserGroups
from django.template.loader import render_to_string
from publications.utils import validate_video
from notifications.signals import notify


def upload_image_group_publication(instance, filename):
    """
    Funcion para calcular la ruta
    donde se almacenaran las imagenes
    de una publicacion
    """
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('group_publications/images', filename)


def upload_video_group_publication(instance, filename):
    """
    Funcion para calcular la ruta
    donde se almacenaran las imagenes
    de una publicacion
    """
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('group_publications/videos', filename)


class PublicationGroupVideo(models.Model):
    publication = models.ForeignKey('PublicationGroup', related_name='videos', on_delete=models.CASCADE)
    video = models.FileField(upload_to=upload_video_group_publication, validators=[validate_video])


class PublicationGroupImage(models.Model):
    publication = models.ForeignKey('PublicationGroup', related_name='images', on_delete=models.CASCADE)
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
    publication = models.OneToOneField('PublicationGroup', related_name='group_extra_content', on_delete=models.CASCADE)


class PublicationGroup(PublicationBase):
    author = models.ForeignKey(User)
    board_group = models.ForeignKey(UserGroups, db_index=True)
    parent = models.ForeignKey('self', blank=True, null=True,
                               related_name='reply_group')
    user_give_me_like = models.ManyToManyField(User, blank=True,
                                               related_name='likes_group_publication')
    user_give_me_hate = models.ManyToManyField(User, blank=True,
                                               related_name='hates_group_publication')

    class Meta:
        unique_together = ('board_group', 'id')

    class MPTTMeta:
        order_insertion_by = ['-created']

    def __str__(self):
        return self.content

    @property
    def blog_channel(self):
        return "group-publication-%d" % self.id

    def has_extra_content(self):
        return hasattr(self, 'group_extra_content')

    def parse_extra_content(self):
        # Buscamos en el contenido del mensaje una URL y mostramos un breve resumen de ella
        link_url = re.findall(
            r'(?:(?:https?|ftp)://)(?:\S+(?::\S*)?@)?(?:(?!(?:10|127)(?:\.\d{1,3}){3})(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)(?:\.(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,})))(?::\d{2,5})?(?:/\S*)?',
            self.content)

        if link_url and len(link_url) > 0:
            self.event_type = 3
            """
            for u in list(set(link_url)):  # Convertimos URL a hipervinculo
                self.content = self.content.replace(u, '<a href="%s">%s</a>' % (u, u))
            """

    def send_notification(self, request, type="pub", is_edited=False):
        """
         Enviamos a través del socket a todos aquellos usuarios
         que esten visitando el perfil donde se publica el comentario.
        """
        data = {
            'type': 'pub',
            'id': self.id,
            'parent_id': self.parent_id,
            'level': self.level,
            'content': render_to_string(request=request, template_name='channels/new_group_publication.html',
                                        context={'node': self, 'group_profile': self.board_group})
        }

        # Enviamos a todos los usuarios que visitan el perfil
        channel_group(self.board_group.group_channel).send({
            "text": json.dumps(data)
        })

        # TODO: Mezclar templates para ahorrar el render

        data['content'] = render_to_string(request=request, template_name='channels/new_group_publication_detail.html',
                                           context={'node': self, 'group_profile': self.board_group})

        # Enviamos por el socket de la publicacion
        if is_edited:
            channel_group(self.blog_channel).send({
                'text': json.dumps(data)
            })

        # Enviamos al blog de la publicacion
        [channel_group("group-publication-%d" % x).send({
            "text": json.dumps(data)
        }) for x in self.get_ancestors().values_list('id', flat=True)]

        # Notificamos al board_owner de la publicacion
        if self.author_id != self.board_group.owner_id:
            notify.send(self.author, actor=self.author.username,
                        recipient=self.board_group.owner,
                        verb=u'<a href="/profile/%s">@%s</a> ha publicado en el grupo %s.' %
                             (self.author.username, self.author.username, self.board_group.name),
                        level='notification_board_group')

            # Enviamos email al board_owner
            send_email.delay(
                "Skyfolk - %s ha comentado en el grupo %s." % (self.author.username, self.board_group.name),
                [self.board_group.owner.email],
                {'to_user': self.board_group.owner.username, 'from_user': self.author.username},
                'emails/new_publication.html')
