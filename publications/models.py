import json
import re
import bleach

from channels import Group
from django.contrib.auth.models import User
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.db import models, transaction
from django.db.models import Q
from taggit.managers import TaggableManager
from photologue.models import Photo
from user_groups.models import UserGroups
from user_profile.models import Relationship
from .utils import get_author_avatar
from user_profile.tasks import send_to_stream
from django.core.exceptions import ObjectDoesNotExist
from notifications.signals import notify
from django.conf import settings
from emoji import Emoji
from mptt.models import MPTTModel, TreeForeignKey

# Los tags HTML que permitimos en los comentarios
ALLOWED_TAGS = bleach.ALLOWED_TAGS + settings.ALLOWED_TAGS
ALLOWED_STYLES = bleach.ALLOWED_STYLES + settings.ALLOWED_STYLES
ALLOWED_ATTRIBUTES = dict(bleach.ALLOWED_ATTRIBUTES)
ALLOWED_ATTRIBUTES.update(settings.ALLOWED_ATTRIBUTES)


class PublicationManager(models.Manager):
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
        pubs = self.filter(author=author_pk, parent=None, deleted=False).order_by(
            'created').reverse()

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
        pubs = self.filter(Q(author=user_pk) & Q(board_owner=user_pk),
                           author=user_pk, deleted=False)

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

    def get_friend_publications(self, user_pk):
        # Obtiene las publicaciones de todos los seguidos por un usuario
        relation = Relationship.objects.filter(Q(from_person=user_pk) & Q(status=1))
        pubs = self.filter(author__profile__to_people__in=relation, deleted=False).order_by('created').reverse()
        return pubs

    def tag_list(self, obj):
        """
        Devuelve los tags de una publicación
        """
        return u", ".join(o.name for o in obj.tags.all())


class PublicationBase(MPTTModel):
    content = models.TextField(blank=False, null=True, max_length=500)
    image = models.ImageField(upload_to='publicationimages',
                              verbose_name='Image', blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    tags = TaggableManager(blank=True)
    deleted = models.BooleanField(default=False, blank=True)

    class Meta:
        abstract = True

    class MPTTMeta:
        order_insertion_by = ['-created']


class Publication(PublicationBase):
    """
    Modelo para las publicaciones de usuario (en perfiles de usuarios)
    """
    author = models.ForeignKey(User, null=True)
    board_owner = models.ForeignKey(User, related_name='board_owner')
    user_give_me_like = models.ManyToManyField(User, blank=True,
                                               related_name='likes_me')
    user_give_me_hate = models.ManyToManyField(User, blank=True,
                                               related_name='hates_me')
    user_share_me = models.ManyToManyField(User, blank=True,
                                           related_name='share_me')
    parent = TreeForeignKey('self', blank=True, null=True,
                            related_name='reply', db_index=True)

    objects = PublicationManager()

    def __str__(self):
        return self.content

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

            privacity = recipientprofile.profile.is_visible(self.author.profile)
            if privacity and privacity != 'all':
                continue

            if self.author.pk != recipientprofile.pk:
                notify.send(self.author, actor=self.author.username,
                            recipient=recipientprofile,
                            verb=u'¡te ha mencionado en su tablón!',
                            description='<a href="%s">Ver</a>' % ('/publication/' + str(self.id)))

            self.content = self.content.replace(mencion,
                                                '<a href="/profile/%s">%s</a>' %
                                                (mencion[1:], mencion))

    def parse_content(self):
        """
        Parseamos el contenido en busca de
        tags html no permitidos y los eliminamos
        """
        self.content = Emoji.replace(self.content)
        self.content = self.content.replace('\n', '').replace('\r', '')
        self.content = bleach.clean(self.content, tags=ALLOWED_TAGS,
                                    attributes=ALLOWED_ATTRIBUTES, styles=ALLOWED_STYLES)

    def send_notification(self, type="pub", is_edited=False):
        """
         Enviamos a través del socket a todos aquellos usuarios
         que esten visitando el perfil donde se publica el comentario.
        """
        if type == "pub":
            id_parent = ''
        else:
            id_parent = self.parent.id

        notification = {
            "id": self.id,
            "content": self.content,
            "avatar_path": get_author_avatar(authorpk=self.author.id),
            "author_username": self.author.username,
            "author_first_name": self.author.first_name,
            "author_last_name": self.author.last_name,
            "created": naturaltime(self.created),
            "type": type,
            "parent": id_parent,
        }
        if is_edited:
            notification['is_edited'] = True
        # Enviamos a todos los usuarios que visitan el perfil
        Group(self.board_owner.profile.group_name).send({
            "text": json.dumps(notification)
        })

    @transaction.atomic
    def save(self, new_comment=False, is_edited=False, *args, **kwargs):
        super(Publication, self).save(*args, **kwargs)

        if new_comment and not self.deleted and not self.parent:
            self.send_notification(is_edited=is_edited)
        elif new_comment and not self.deleted:
            self.send_notification(type="reply", is_edited=is_edited)

        # Enviamos al tablon de noticias (inicio)
        if new_comment and self.author == self.board_owner:
            send_to_stream.delay(self.author.id, self.id)


class PublicationGroup(PublicationBase):
    g_author = models.ForeignKey(User, null=True)
    board_group = models.ForeignKey(UserGroups, related_name='board_group')
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

    def __str__(self):
        return self.content

    def add_hashtag(self):
        """
        Añadimos los hashtags encontrados a la
        lista de tags => atributo "tags"
        """
        hashtags = [tag.strip() for tag in self.content.split() if tag.startswith("#")]
        print('>>> HASHTAGS')
        print(hashtags)
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
            "avatar_path": get_author_avatar(authorpk=self.author),
            "author_username": self.author.username,
            "author_first_name": self.author.first_name,
            "author_last_name": self.author.last_name,
            "created": naturaltime(self.created),
            "type": type,
            "parent": id_parent,
        }
        # Enviamos a todos los usuarios que visitan el perfil
        Group(self.board_photo.group_name).send({
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
    image = models.ImageField(verbose_name='publication_deleted_image', blank=True, null=True)
    created = models.DateTimeField(null=True)
