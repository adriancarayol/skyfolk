import json
import re
import bleach
import requests
import uuid
import os

from channels import Group as channel_group
from django.contrib.auth.models import User, Group
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.db import models, transaction
from django.db.models import Q
from taggit.managers import TaggableManager
from photologue.models import Photo
from user_profile.models import NodeProfile
from .utils import get_author_avatar
from user_profile.tasks import send_to_stream
from django.core.exceptions import ObjectDoesNotExist
from notifications.signals import notify
from django.conf import settings
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext as _
from bs4 import BeautifulSoup
from embed_video.fields import EmbedVideoField
from embed_video.backends import detect_backend, EmbedVideoException
from user_profile.utils import group_name
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings

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
    publication = models.ForeignKey('Publication', related_name='publication_extra_content')


class SharedPublication(models.Model):
    """
    Modelo para comparticiones compartidas (copiadas de un skyline a otro)
    """
    by_user = models.ForeignKey(User, related_name='shared_by_user')
    created = models.DateTimeField(auto_now_add=True)
    publication = models.ForeignKey('Publication', null=True)

    class Meta:
        unique_together = ('by_user', 'publication')


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
        (6, _("shared"))
    )
    author = models.ForeignKey(User, null=True)
    board_owner = models.ForeignKey(User, related_name='board_owner')
    user_give_me_like = models.ManyToManyField(User, blank=True,
                                               related_name='likes_me')
    user_give_me_hate = models.ManyToManyField(User, blank=True,
                                               related_name='hates_me')
    shared_publication = models.ForeignKey(SharedPublication, blank=True, null=True,
                                           related_name='share_me')
    parent = TreeForeignKey('self', blank=True, null=True,
                            related_name='reply', db_index=True)
    event_type = models.IntegerField(choices=EVENT_CHOICES, default=1)
    extra_content = models.ForeignKey(ExtraContent, null=True, related_name='extra_content')

    # objects = PublicationManager()

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
        return SharedPublication.objects.filter(publication=self).count()

    def add_hashtag(self):
        """
        Añadimos los hashtags encontramos a la
        lista de tags => atributo "tags"
        """
        hashtags = [tag.strip() for tag in self.content.split() if tag.startswith("#")]
        hashtags = set(hashtags)
        for tag in hashtags:
            if tag.endswith((',', '.')):
                tag = tag[:-1]
            self.tags.add(tag)
            self.content = self.content.replace(tag,
                                                '<a href="/search/">{0}</a>'.format(tag))

    def parse_mentions(self):
        """
        Buscamos menciones en el contenido del mensaje
        y enviamos un mensaje al usuario
        """
        menciones = re.findall('\\@[a-zA-Z0-9_]+', self.content)
        menciones = set(menciones)
        for mencion in menciones:
            try:
                recipientprofile = User.objects.get(username=mencion[1:])
            except ObjectDoesNotExist:
                continue

            self.content = self.content.replace(mencion,
                                                '<a href="/profile/%s">%s</a>' %
                                                (mencion[1:], mencion))

            if self.author.pk != recipientprofile.pk:
                try:
                    n = NodeProfile.nodes.get(user_id=self.author_id)
                    m = NodeProfile.nodes.get(user_id=recipientprofile.id)
                except Exception:
                    continue

                privacity = m.is_visible(n)

                if privacity and privacity != 'all':
                    continue

                notify.send(self.author, actor=self.author.username,
                            recipient=recipientprofile,
                            verb=u'¡te ha mencionado!',
                            description='<a href="%s">Ver</a>' % ('/publication/' + str(self.id)))

    def parse_content(self):
        """
        Parseamos el contenido en busca de
        tags html no permitidos y los eliminamos
        """
        self.content = self.content.replace('\n', '').replace('\r', '')
        self.content = bleach.clean(self.content, tags=ALLOWED_TAGS,
                                    attributes=ALLOWED_ATTRIBUTES, styles=ALLOWED_STYLES)
        # Buscamos el el contenido del mensaje una URL y mostramos un breve resumen de ella
        link_url = re.findall(
            r'(?:(?:https?|ftp)://)(?:\S+(?::\S*)?@)?(?:(?!(?:10|127)(?:\.\d{1,3}){3})(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)(?:\.(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,})))(?::\d{2,5})?(?:/\S*)?',
            self.content)

        try:
            backend = detect_backend(link_url[-1]) # youtube o soundcloud
        except (EmbedVideoException, IndexError) as e:
            backend = None

        if link_url and len(link_url) > 0 and backend:
            for u in list(set(link_url)):  # Convertimos URL a hipervinculo
                self.content = self.content.replace(u, '<a href="%s">%s</a>' % (u, u))
            self.event_type = 3
            extra_c, created = ExtraContent.objects.get_or_create(publication=self, video=link_url[-1])
            self.extra_content = extra_c
        elif link_url and len(link_url) > 0:
            for u in list(set(link_url)):  # Convertimos URL a hipervinculo
                self.content = self.content.replace(u, '<a href="%s">%s</a>' % (u, u))

            url = link_url[-1]  # Get last url
            response = requests.get(url)
            soup = BeautifulSoup(response.text)
            # First get the meta description tag
            description = soup.find('meta', attrs={'name': 'og:description'}) or soup.find('meta', attrs={
                'property': 'og:description'}) or soup.find('meta', attrs={'name': 'description'})
            title = soup.find('meta', attrs={'name': 'og:title'}) or soup.find('meta', attrs={
                'property': 'og:title'}) or soup.find('meta', attrs={'name': 'title'})
            image = soup.find('meta', attrs={'name': 'og:image'}) or soup.find('meta', attrs={
                'property': 'og:image'}) or soup.find('meta', attrs={'name': 'image'})

            self.event_type = 3
            extra_c, created = ExtraContent.objects.get_or_create(url=url, publication=self)
            if description:
                extra_c.description = description.get('content', None)[:265]
            if title:
                extra_c.title = title.get('content', None)[:63]
            if image:
                extra_c.image = image.get('content', None)
            extra_c.save()
            self.extra_content = extra_c
        else:
            self.extra_content = None

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
            author_parent = self.parent.author.username
            avatar_parent = get_author_avatar(self.parent.author.id)

        extra_c = self.extra_content

        have_extra_content = False
        if extra_c:
            have_extra_content = True

        notification = {
            "id": self.id,
            "content": self.content,
            "avatar_path": get_author_avatar(authorpk=self.author.id),
            "author_id": self.author_id,
            "board_owner_id": self.board_owner_id,
            "author_username": self.author.username,
            "author_first_name": self.author.first_name,
            "author_last_name": self.author.last_name,
            "created": naturaltime(self.created),
            "type": type,
            "parent": id_parent,
            "level": self.get_level(),
            'is_edited': is_edited,
            'token': csrf_token,
            'event_type': self.event_type,
            'extra_content': have_extra_content,
            'parent_author': author_parent,
            'images': list(self.images.all().values('image')),
            'parent_avatar': avatar_parent,
        }

        if have_extra_content:
            notification['extra_content_title'] = extra_c.title
            notification['extra_content_description'] = extra_c.description
            notification['extra_content_image'] = extra_c.image
            notification['extra_content_url'] = extra_c.url

        # Enviamos a todos los usuarios que visitan el perfil
        channel_group(group_name(self.board_owner_id)).send({
            "text": json.dumps(notification)
        })

    def save(self, csrf_token=None, new_comment=False, is_edited=False, *args, **kwargs):
        super(Publication, self).save(*args, **kwargs)

        if new_comment:
            if not self.deleted:
                self.send_notification(csrf_token=csrf_token, is_edited=is_edited)  # Enviar publicacion por socket

        # Enviamos al tablon de noticias (inicio)
        if new_comment and self.author == self.board_owner:
            send_to_stream.delay(self.author_id, self.id)




def validate_video(value):
    ''' if value.file is an instance of InMemoryUploadedFile, it means that the
    file was just uploaded with this request (i.e., it's a creation process,
    not an editing process. '''
    if isinstance(value.video, InMemoryUploadedFile) and value.file.content_type.split('/')[1] not in settings.VIDEO_EXTENTIONS:
        raise ValueError('Please upload a valid video file')

class PublicationVideo(models.Model):
    publication = models.ForeignKey(Publication, related_name='videos')
    video = models.FileField(upload_to=upload_video_publication, validators=[validate_video])


class PublicationImage(models.Model):
    publication = models.ForeignKey(Publication, related_name='images')
    image = models.ImageField(upload_to=upload_image_publication)


class PublicationGroup(PublicationBase):
    g_author = models.ForeignKey(User, null=True)
    board_group = models.ForeignKey(Group, related_name='board_group')
    user_give_me_like = models.ManyToManyField(User, blank=True,
                                               related_name='likes_group_me')
    user_give_me_hate = models.ManyToManyField(User, blank=True,
                                               related_name='hates_group_me')
    user_share_me = models.ManyToManyField(User, blank=True,
                                           related_name='share_group_me')
    parent = models.ForeignKey('self', blank=True, null=True,
                               related_name='reply_group')

    # TODO objects = PublicationManager()

    def __str__(self):
        return self.content


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

    def send_notification(self, type="pub"):
        """
         Enviamos a través del socket a todos aquellos usuarios
         que esten visitando el perfil donde se publica el comentario.
        """
        if type == "pub":
            id_parent = ''
        else:
            id_parent = self.parent.id

        notification = {
            "id": self.pk,
            "content": self.content,
            "avatar_path": get_author_avatar(authorpk=self.p_author_id),
            "author_username": self.p_author.username,
            "author_first_name": self.p_author.first_name,
            "author_last_name": self.p_author.last_name,
            "created": naturaltime(self.created),
            "type": type,
            "parent": id_parent,
        }
        # Enviamos a todos los usuarios que visitan el perfil
        channel_group(self.board_photo.group_name).send({
            "text": json.dumps(notification)
        })

    def save(self, new_comment=False, *args, **kwargs):
        if new_comment:
            result = super(PublicationPhoto, self).save(*args, **kwargs)
            self.add_hashtag()
            if not self.parent:
                self.send_notification()
            else:
                self.send_notification(type="reply")
            return result
        else:
            super(PublicationPhoto, self).save(*args, **kwargs)


class PublicationDeleted(models.Model):
    """
    Contiene las publicaciones eliminadas por los usuarios
    """
    author = models.ForeignKey(User, null=True)
    content = models.TextField(blank=False, null=True, max_length=500)
    created = models.DateTimeField(null=True)
