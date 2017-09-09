import json
import os
import re
import uuid

import bleach
from channels import Group as channel_group
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from embed_video.fields import EmbedVideoField
from mptt.models import MPTTModel, TreeForeignKey
from taggit.managers import TaggableManager

from notifications.signals import notify
from photologue.models import Photo
from publications.utils import validate_video
from user_profile.tasks import send_email
from user_profile.utils import group_name
from .utils import get_channel_name

# Los tags HTML que permitimos en los comentarios
ALLOWED_TAGS = bleach.ALLOWED_TAGS + settings.ALLOWED_TAGS
ALLOWED_STYLES = bleach.ALLOWED_STYLES + settings.ALLOWED_STYLES
ALLOWED_ATTRIBUTES = dict(bleach.ALLOWED_ATTRIBUTES)
ALLOWED_ATTRIBUTES.update(settings.ALLOWED_ATTRIBUTES)


class PublicationManager(models.Manager):
    """
    Despreciado
    """
    list_display = ['tag_list']

    # Functions of publications
    def get_publication(self, publicationid):
        return self.objects.get(pk=publicationid)

    def remove_publication(self, publicationid):
        self.objects.get(pk=publicationid).delete()

    def get_authors_publications(self, author_pk):
        # cambiar a nombre mas claro como get_logged_user_publications
        # filtros: from_publication__profile=self -> retorna los comentarios
        # hechos al propietario por amigos o el mismo propietario.
        # from_publication__replies=None -> retorna solo los comentarios padre.
        pubs = self.filter(author=author_pk, parent=None, deleted=False)

        print('>>>>pubs: {}'.format(pubs))

        # Agregar replicas de los comentarios
        # for pub in pubs:
        #     print('pub: {}'.format(pub.id))
        #     reply = self.filter(parent=pub.id).order_by('created')
        #     print('REPLIES: {}'.format(reply))
        #     pub.replies = reply

        return pubs

    def get_user_profile_publications(self, user_pk, board_owner_pk):
        # cambiar a nombre mas claro como get_logged_user_publications
        # filtros: from_publication__profile=self -> retorna los comentarios
        # hechos al propietario por amigos o el mismo propietario.
        # from_publication__replies=None -> retorna solo los comentarios padre.
        # pubs = self.filter(Q(author=user_pk) & Q(board_owner=user_pk),
        #                   author=user_pk, deleted=False)
        pubs = self.filter(board_owner=board_owner_pk)

        print('LONGITUD PUBS: {}'.format(len(pubs)))
        print('>>>>pubs: {}'.format(pubs))

        # Agregar replicas de los comentarios
        # for pub in pubs:
        #     print('pub: {}'.format(pub.id))
        #     reply = self.filter(parent=pub.id, deleted=False).order_by('created')
        #     print('REPLIES: {}'.format(reply))
        #     pub.replies = reply

        return pubs

    def get_friend_profile_publications(self, user_pk, board_owner_pk):
        # cambiar a nombre mas claro como get_logged_user_publications
        # filtros: from_publication__profile=self -> retorna los comentarios
        # hechos al propietario por amigos o el mismo propietario.
        # from_publication__replies=None -> retorna solo los comentarios padre.
        pubs = self.filter(Q(author=user_pk) | Q(board_owner=board_owner_pk),
                           board_owner=board_owner_pk, deleted=False)

        print('>>>>pubs: {}'.format(pubs))

        # Agregar replicas de los comentarios
        # for pub in pubs:
        #     print('pub: {}'.format(pub.id))
        #     reply = self.filter(parent=pub.id).order_by('created')
        #     print('REPLIES: {}'.format(reply))
        #     pub.replies = reply

        return pubs

    def get_publication_replies(self, user_pk, board_owner_pk, parent):
        # cambiar a nombre mas claro como get_logged_user_publications
        # filtros: a) user_pk -> clave del autor de la publicacion. B) board_
        # owner_pk -> clave del propietario del perfil donde se publica. C) pa-
        # rent -> clave del padre de la replica.
        pubs = self.filter(Q(author=user_pk) & Q(board_owner=board_owner_pk),
                           board_owner=board_owner_pk, parent=parent, deleted=False).order_by(
            'created').reverse()

        return pubs

    def tag_list(self, obj):
        """
        Devuelve los tags de una publicación
        """
        return u", ".join(o.name for o in obj.tags.all())


def upload_image_publication(instance, filename):
    """
    Funcion para calcular la ruta
    donde se almacenaran las imagenes
    de una publicacion
    """
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('publications/images', filename)


def upload_video_publication(instance, filename):
    """
    Funcion para calcular la ruta
    donde se almacenaran las imagenes
    de una publicacion
    """
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('skyfolk/media/publications/videos', filename)


class PublicationBase(MPTTModel):
    content = models.TextField(blank=False, null=True, max_length=500)
    created = models.DateTimeField(auto_now_add=True, null=True)
    tags = TaggableManager(blank=True)
    deleted = models.BooleanField(default=False, blank=True)

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
        return self.get_descendants().filter(level__lte=1, deleted=False).count()

    def get_descendants_not_deleted(self):
        return self.get_descendants().filter(deleted=False).count()

    def add_hashtag(self):
        """
        Añadimos los hashtags encontramos a la
        lista de tags => atributo "tags"
        """
        hashtags = set([tag.strip() for tag in self.content.split() if tag.startswith("#")])

        for tag in hashtags:
            if tag.endswith((',', '.')):
                tag = tag[:-1]
            self.content = self.content.replace(tag,
                                                '<a href="/user-search/?q={0}">{1}</a>'.format(tag[1:], tag))

    def parse_mentions(self):
        """
        Buscamos menciones en el contenido del mensaje
        y enviamos un mensaje al usuario
        """
        menciones = re.findall('\\@[a-zA-Z0-9_]+', self.content)
        menciones = set(menciones)
        for mencion in menciones:
            self.content = self.content.replace(mencion,
                                                '<a href="/profile/%s">%s</a>' %
                                                (mencion[1:], mencion))

    def parse_content(self):
        """
        Parseamos el contenido en busca de
        tags html no permitidos y los eliminamos
        """
        self.content = self.content.replace('\n', '').replace('\r', '')
        """
        self.content = bleach.clean(self.content, tags=ALLOWED_TAGS,
                                    attributes=ALLOWED_ATTRIBUTES, styles=ALLOWED_STYLES)
        """
        self.content = bleach.clean(self.content, tags=['a'])
        self.parse_extra_content()

        """
        bold = re.findall('\*[^\*]+\*', self.content)
        bold = list(set(bold))

        for b in bold:
            self.content = self.content.replace(b, '<b>%s</b>' % (b[1:len(b) - 1]))

        italic = re.findall('~[^~]+~', self.content)
        italic = list(set(italic))
        for i in italic:
            self.content = self.content.replace(i, '<i>%s</i>' % (i[1:len(i) - 1]))

        tachado = re.findall('\^[^\^]+\^', self.content)
        tachado = list(set(tachado))
        for i in tachado:
            self.content = self.content.replace(i, '<strike>%s</strike>' % (i[1:len(i) - 1]))
        """

    def parse_extra_content(self):
        pass


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
    publication = models.OneToOneField('Publication', related_name='extra_content')


class Publication(PublicationBase):
    """
    Modelo para las publicaciones de usuario (en perfiles de usuarios)
    """
    EVENT_CHOICES = (
        (1, _("publication")),
        (2, _("new_relation")),
        (3, _("link")),
        (4, _("relevant")),
        (5, _("image")),
        (6, _("shared")),
        (7, _("shared_photo_pub")),
        (8, _("shared_group_pub")),
    )
    # TODO: Eliminar null=True de author...
    author = models.ForeignKey(User, null=True)
    board_owner = models.ForeignKey(User, related_name='board_owner', db_index=True)
    user_give_me_like = models.ManyToManyField(User, blank=True,
                                               related_name='likes_me')
    user_give_me_hate = models.ManyToManyField(User, blank=True,
                                               related_name='hates_me')
    shared_publication = models.ForeignKey('self', blank=True, null=True)
    shared_photo_publication = models.ForeignKey('publications_gallery.PublicationPhoto', blank=True, null=True)
    shared_group_publication = models.ForeignKey('publications_groups.PublicationGroup', blank=True, null=True)
    parent = TreeForeignKey('self', blank=True, null=True,
                            related_name='reply', db_index=True)
    event_type = models.IntegerField(choices=EVENT_CHOICES, default=1)

    # objects = PublicationManager()

    class Meta:
        unique_together = (('shared_photo_publication', 'id'),
                           ('shared_publication', 'id'),
                           ('board_owner', 'id'))

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
        return Publication.objects.filter(shared_publication_id=self.id, deleted=False).count()

    def has_extra_content(self):
        return hasattr(self, 'extra_content')

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
            'content': render_to_string(request=request, template_name='channels/new_publication.html',
                                        context={'node': self, 'user_profile': self.board_owner})
        }

        # Enviamos a todos los usuarios que visitan el perfil
        channel_group(group_name(self.board_owner_id)).send({
            "text": json.dumps(data)
        })

        # TODO: Mezclar templates para ahorrar el render
        data['content'] = render_to_string(request=request, template_name='channels/new_publication_detail.html',
                                           context={'node': self, 'user_profile': self.board_owner})

        # Enviamos por el socket de la publicacion
        if is_edited:
            channel_group(get_channel_name(self.id)).send({
                'text': json.dumps(data)
            })

        # Enviamos al blog de la publicacion
        [channel_group(get_channel_name(x)).send({
            "text": json.dumps(data)
        }) for x in self.get_ancestors().values_list('id', flat=True)]

        # Notificamos al board_owner de la publicacion
        if self.author_id != self.board_owner_id:
            notify.send(self.author, actor=self.author.username,
                        recipient=self.board_owner,
                        verb=u'<a href="/profile/%s">@%s</a> ha publicado en tu tablón.' %
                             (self.author.username, self.author.username), level='notification_board_owner')

            # Enviamos email al board_owner
            send_email.delay("Skyfolk - %s ha comentado en tu skyline." % self.author.username,
                             [self.board_owner.email],
                             {'to_user': self.board_owner.username, 'from_user': self.author.username},
                             'emails/new_publication.html')


class PublicationVideo(models.Model):
    publication = models.ForeignKey(Publication, related_name='videos')
    video = models.FileField(upload_to=upload_video_publication, validators=[validate_video])


class PublicationImage(models.Model):
    publication = models.ForeignKey(Publication, related_name='images')
    image = models.ImageField(upload_to=upload_image_publication)


class PublicationDeleted(models.Model):
    """
    Contiene las publicaciones eliminadas por los usuarios
    """
    TYPE_PUBLICATIONS = (
        (1, _("skyline")),
        (2, _("photo")),
    )
    author = models.ForeignKey(User, null=True)
    content = models.TextField(blank=False, null=True, max_length=500)
    created = models.DateTimeField(null=True)
    type_publication = models.IntegerField(choices=TYPE_PUBLICATIONS, default=1)
