from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from user_profile.models import Relationship
from channels import Group
from avatar.models import Avatar
from django.conf import settings
from django.contrib.humanize.templatetags.humanize import naturaltime

import json

class PublicationManager(models.Manager):
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

    def get_author_avatar(self, authorpk):
        """
        Devuelve el avatar del autor de la publicacion pasada como parametro
        """
        actor_avatar = ''
        try:
            avatars = Avatar.objects.filter(user=authorpk)
            for avatar in avatars:
                if avatar.primary:
                    actor_avatar = avatar.get_absolute_url()
        except Avatar.DoesNotExist:
            actor_avatar = settings.STATIC_URL + 'img/nuevo.png' # default avatar

        return actor_avatar

class Publication(models.Model):
    content = models.TextField(blank=False)
    author = models.ForeignKey(User, related_name='publications')
    board_owner = models.ForeignKey(User, related_name='board_owner')
    image = models.ImageField(upload_to='publicationimages',
                              verbose_name='Image', blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    user_give_me_like = models.ManyToManyField(User, blank=True,
                                               related_name='likes_me')
    user_give_me_hate = models.ManyToManyField(User, blank=True,
                                               related_name='hates_me')
    user_share_me = models.ManyToManyField(User, blank=True,
                                           related_name='share_me')
    parent = models.ForeignKey('self', blank=True, null=True,
                               related_name='reply')
    objects = PublicationManager()

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.content

    def send_notification(self):
        """
         Enviamos a través del socket a todos aquellos usuarios
         que esten visitando el perfil donde se publica el comentario.
        """
        notification = {
            "id": self.pk,
            "content": self.content,
            "avatar_path": Publication.objects.get_author_avatar(authorpk=self.author),
            "author_username": self.author.username,
            "author_first_name": self.author.first_name,
            "author_last_name": self.author.last_name,
            "created": naturaltime(self.created),
        }
        # Enviamos a todos los usuarios que visitan el perfil
        Group(self.board_owner.profile.group_name).send({
                "text": json.dumps(notification)
            })

    def save(self, *args, **kwargs):
        print('NOTIFICACION ENVIADA POR EL SOCKET...')
        result = super(Publication, self).save(*args, **kwargs)
        self.send_notification()
        return result
