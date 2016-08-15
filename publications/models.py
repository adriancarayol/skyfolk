from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q


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
