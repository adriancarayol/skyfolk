import json
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from user_profile.models import Relationship
from channels import Group
from django.contrib.humanize.templatetags.humanize import naturaltime
from .utils import get_author_avatar
from taggit.managers import TaggableManager
from text_processor.format_text import TextProcessor
from user_groups.models import UserGroups
from photologue.models import Photo


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
        pubs = self.filter(author=author_pk, parent=None).order_by(
            'created').reverse()

        print('>>>>pubs: {}'.format(pubs))

        # Agregar replicas de los comentarios
        for pub in pubs:
            print('pub: {}'.format(pub.id))
            reply = self.filter(parent=pub.id).order_by('created')
            print('REPLIES: {}'.format(reply))
            pub.replies = reply

        return pubs

    def get_user_profile_publications(self, user_pk, board_owner_pk):
        # cambiar a nombre mas claro como get_logged_user_publications
        # filtros: from_publication__profile=self -> retorna los comentarios
        # hechos al propietario por amigos o el mismo propietario.
        # from_publication__replies=None -> retorna solo los comentarios padre.
        pubs = self.filter(Q(author=user_pk) & Q(board_owner=user_pk),
                           author=user_pk, parent=None).order_by('created') \
            .reverse()

        print('>>>>pubs: {}'.format(pubs))

        # Agregar replicas de los comentarios
        for pub in pubs:
            print('pub: {}'.format(pub.id))
            reply = self.filter(parent=pub.id).order_by('created')
            print('REPLIES: {}'.format(reply))
            pub.replies = reply

        return pubs

    def get_friend_profile_publications(self, user_pk, board_owner_pk):
        # cambiar a nombre mas claro como get_logged_user_publications
        # filtros: from_publication__profile=self -> retorna los comentarios
        # hechos al propietario por amigos o el mismo propietario.
        # from_publication__replies=None -> retorna solo los comentarios padre.
        pubs = self.filter(Q(author=user_pk) | Q(board_owner=board_owner_pk),
                           board_owner=board_owner_pk, parent=None).order_by(
            'created').reverse()

        print('>>>>pubs: {}'.format(pubs))

        # Agregar replicas de los comentarios
        for pub in pubs:
            print('pub: {}'.format(pub.id))
            reply = self.filter(parent=pub.id).order_by('created')
            print('REPLIES: {}'.format(reply))
            pub.replies = reply

        return pubs

    def get_publication_replies(self, user_pk, board_owner_pk, parent):
        # cambiar a nombre mas claro como get_logged_user_publications
        # filtros: a) user_pk -> clave del autor de la publicacion. B) board_
        # owner_pk -> clave del propietario del perfil donde se publica. C) pa-
        # rent -> clave del padre de la replica.
        pubs = self.filter(Q(author=user_pk) & Q(board_owner=board_owner_pk),
                           board_owner=board_owner_pk, parent=parent).order_by(
            'created').reverse()

        return pubs

    def get_friend_publications(self, user_pk):
        # Obtiene las publicaciones de todos los seguidos por un usuario
        relation = Relationship.objects.filter(Q(from_person=user_pk) & Q(status=1))
        pubs = self.filter(author__profile__to_people__in=relation).order_by('created').reverse()
        return pubs

    def tag_list(self, obj):
        """
        Devuelve los tags de una publicación
        """
        return u", ".join(o.name for o in obj.tags.all())


class PublicationBase(models.Model):
    content = models.TextField(blank=False, null=True)
    image = models.ImageField(upload_to='publicationimages',
                              verbose_name='Image', blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    tags = TaggableManager(blank=True)

    class Meta:
        abstract = True
        ordering = ('-created',)



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
    parent = models.ForeignKey('self', blank=True, null=True,
                               related_name='reply')

    objects = PublicationManager()

    def __str__(self):
        return self.content

    def add_hashtag(self):
        """
        Añadimos los hashtags encontramos a la
        lista de tags => atributo "tags"
        """
        hashtags = [tag.strip() for tag in self.content.split() if tag.startswith("#")]
        print('>>> HASHTAGS')
        print(hashtags)
        for tag in hashtags:
            if tag.endswith((',', '.')):
                tag = tag[:-1]
            self.tags.add(tag)
        self.content = TextProcessor.get_format_text(self.content, self.author, hashtags)

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
        Group(self.board_owner.profile.group_name).send({
                "text": json.dumps(notification)
            })

    def save(self, new_comment=False, *args, **kwargs):
        if new_comment:
            print('NOTIFICACION ENVIADA POR EL SOCKET...')
            result = super(Publication, self).save(*args, **kwargs)
            self.add_hashtag()
            if not self.parent:
                self.send_notification()
            else:
                self.send_notification(type="reply")
            return result
        else:
            super(Publication, self).save(*args, **kwargs)

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


    #TODO objects = PublicationManager()

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
        Añadimos los hashtags encontramos a la
        lista de tags => atributo "tags"
        """
        hashtags = [tag.strip() for tag in self.content.split() if tag.startswith("#")]
        print('>>> HASHTAGS')
        print(hashtags)
        for tag in hashtags:
            if tag.endswith((',', '.')):
                tag = tag[:-1]
            self.tags.add(tag)
        self.content = TextProcessor.get_format_text(self.content, self.p_author, hashtags)

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
            print('NOTIFICACION ENVIADA POR EL SOCKET...')
            result = super(PublicationPhoto, self).save(*args, **kwargs)
            self.add_hashtag()
            if not self.parent:
                self.send_notification()
            else:
                self.send_notification(type="reply")
            return result
        else:
            super(PublicationPhoto, self).save(*args, **kwargs)

