from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
import publications
import timeline
from notifications.models import Notification

# from publications.models import Publication
# from _overlapped import NULL
RELATIONSHIP_FOLLOWING = 1
RELATIONSHIP_FOLLOWER = 2
RELATIONSHIP_BLOCKED = 3
RELATIONSHIP_STATUSES = (
    (RELATIONSHIP_FOLLOWING, 'Following'),
    (RELATIONSHIP_FOLLOWER, 'Follower'),
    (RELATIONSHIP_BLOCKED, 'Blocked'),
)

REQUEST_FOLLOWING = 1
REQUEST_FOLLOWER = 2
REQUEST_BLOCKED = 3
REQUEST_STATUSES = (
    (REQUEST_FOLLOWING, 'Following'),
    (REQUEST_FOLLOWER, 'Follower'),
    (REQUEST_BLOCKED, 'Blocked'),
)



def uploadAvatarPath(instance, filename):
    return '%s/avatar/%s' % (instance.user.username, filename)


def uploadBackImagePath(instance, filename):
    return '%s/backImage/%s' % (instance.user.username, filename)


class UserProfile(models.Model):
    PIN_LENGTH = 9

    """
    Diferentes opciones de privacidad para el usuario
    """
    ONLYFOLLOWERS = 'OF'
    ONLYFOLLOWERSANDFOLLOWS = 'OFAF'
    ALL = 'A'
    NOTHING = 'N'
    OPTIONS_PRIVACITY = (
        (ONLYFOLLOWERS, 'OnlyFo'),
        (ONLYFOLLOWERSANDFOLLOWS, 'OnlyFAF'),
        (ALL, 'All'),
        (NOTHING, 'Nothing'),
    )

    user = models.OneToOneField(User, unique=True, related_name='profile')
    backImage = models.ImageField(upload_to=uploadBackImagePath, verbose_name='BackImage', blank=True, null=True)
    relationships = models.ManyToManyField('self', through='Relationship', symmetrical=False, related_name='related_to')
    likeprofiles = models.ManyToManyField('self', through='LikeProfile', symmetrical=False, related_name='likesToMe')
    requests = models.ManyToManyField('self', through='Request', symmetrical=False, related_name='requestsToMe')
    timeline = models.ManyToManyField('self', through='timeline.Timeline', symmetrical=False,
                                      related_name='timeline_to')
    status = models.CharField(max_length=20, null=True, verbose_name='estado')
    ultimosUsuariosVisitados = models.ManyToManyField('self')  # Lista de ultimos usuarios visitados.
    hiddenMenu = models.BooleanField(
        default=True)  # Para que el usuario decida que menu le gustaria tener, si el oculto o el estático.
    privacity = models.CharField(max_length=4,
                                 choices=OPTIONS_PRIVACITY, default=ALL)  # Privacidad del usuario (por defecto ALL)
    """
        El usuario decide si es necesario recibir una solicitud
        de seguimiento, o directamente se puede añadir como seguido
        por otro usuario.
    """
    need_follow_confirmation = models.BooleanField(default=True)


    def __unicode__(self):
        return "{}'s profile".format(self.user.username)

    class Meta:
        db_table = 'user_profile'

    """
    def account_verified(self):
        if self.user.is_authenticated:
            result = EmailAddress.objects.filter(email=self.user.email)
            if len(result):
                return result[0].verified
        return False
    """
    """
    def save(self, *args, **kwargs):
        # delete old image when replacing by updating the file
        try:
            this = UserProfile.objects.get(id=self.id)
            if this.image != self.image:
                this.image.delete(save=False)
        except:
            pass  # when new photo then we do nothing, normal case
        super(UserProfile, self).save(*args, **kwargs)
    """

    # Methods of relationships between users
    def add_relationship(self, person, status, symm=False):
        print('>>>>>>> add_relationship')
        relationship, created = Relationship.objects.get_or_create(from_person=self, to_person=person, status=status)
        print('>>>>>>> created')
        print(created)
        if symm:
            # avoid recursion by passing 'symm=False'
            person.add_relationship(self, status, False)
        return relationship

    def remove_relationship(self, person, status, symm=False):
        Relationship.objects.filter(from_person=self, to_person=person, status=status).delete()
        if symm:
            # avoid recursion by passing 'symm=False'
            person.remove_relationship(self, status, False)

    def get_relationships(self, status):
        return self.relationships.filter(
            to_people__status=status,
            to_people__from_person=self)

    def get_related_to(self, status):
        return self.related_to.filter(
            from_people__status=status,
            from_people__to_person=self)

    def is_visible(self, user_pk):
        """
        Devuelve si el perfil que estamos visitando
        es visible por nosotros.
        :param user_pk:
        :return booleano que determina si el perfil es visible:
        """

        # Si el perfil esta bloqueado
        if self.is_blocked(user_pk):
            return False

        # Si el nivel de privacidad es TODOS
        if self.privacity == UserProfile.ALL:
            return True

        # Recuperamos la relacion de "seguir"
        try:
            relation_follow = Relationship.objects.filter(from_person=self, to_person=user_pk, status=RELATIONSHIP_FOLLOWING)
        except ObjectDoesNotExist:
            relation_follow = None

        # Si el perfil es seguido y tiene la visiblidad "solo seguidores"
        if self.privacity == UserProfile.ONLYFOLLOWERS and relation_follow:
            return True

        # Recuperamos la relacion de "seguidor"
        try:
            relation_follower = Relationship.objects.filter(from_person=self, to_person=user_pk, status=RELATIONSHIP_FOLLOWER)
        except ObjectDoesNotExist:
            relation_follower = None

        # Si la privacidad es "seguidores y/o seguidos" y cumple los requisitos
        if self.privacity == UserProfile.ONLYFOLLOWERSANDFOLLOWS and \
                (relation_follower or relation_follow):
            return True

        # else...
        return False
    # Methods of timeline

    def getTimelineToMe(self):
        return self.timeline_to.filter(
            from_timeline__profile=self).values('user__username', 'from_timeline__publication__content',
                                                'from_timeline__id', 'from_timeline__publication__author__username',
                                                'from_timeline__insertion_date', 'from_timeline__publication__id',
                                                'from_timeline__type', 'from_timeline__verb').order_by(
            'from_timeline__insertion_date').reverse()

    # Old (Mejor usar TimelineManager)
    def remove_timeline(self, timeline_id):
        t = timeline.models.Timeline.objects.get(pk=timeline_id)
        t.publication.user_share_me.remove(self.user)
        t.delete()

    # Methods of publications

    def get_publication(self, publicationid):
        return publications.models.Publication.objects.get(pk=publicationid)

    def remove_publication(self, publicationid):
        publications.models.Publication.objects.get(pk=publicationid).delete()

    def get_publicationsToMe(self):
        return self.publications_to.filter(
            from_publication__profile=self).values('user__username', 'user__first_name', 'user__last_name',
                                                   'from_publication__id',
                                                   'from_publication__content', 'from_publication__created',
                                                   'from_publication__replies')

    def get_publicationsToMeTop15(self):
        return self.publications_to.filter(
            from_publication__profile=self).values('user__username', 'user__first_name', 'user__last_name',
                                                   'from_publication__id',
                                                   'from_publication__content', 'from_publication__created')[0:15]

    def get_myPublications(self):
        return self.publications.filter(
            to_publication__author=self).values('user__username', 'to_publication__profile', 'user__first_name',
                                                'user__last_name',
                                                'from_publication__id', 'to_publication__content',
                                                'to_publication__created', 'to_publication__user_give_me_like')

    # Obtener seguidos
    def get_following(self):
        return self.get_relationships(RELATIONSHIP_FOLLOWING).values('user__id', 'user__username', 'user__first_name',
                                                                     'user__last_name',
                                                                     'user__profile__backImage').order_by('id')

    # Obtener seguidores
    def get_followers(self):
        return self.get_relationships(RELATIONSHIP_FOLLOWER).values('user__id', 'user__username', 'user__first_name',
                                                                    'user__last_name',
                                                                    'user__profile__backImage').order_by('id')

    '''def get_friends(self):
        return self.get_relationships(RELATIONSHIP_FRIEND).values('user__id', 'user__username', 'user__first_name',
                                                                  'user__last_name',
                                                                  'user__profile__backImage').order_by('id')'''
    # methods blocks
    def add_block(self, profile):
        return self.add_relationship(profile, RELATIONSHIP_BLOCKED,
                                     False)

    def get_blockeds(self):
        return self.get_relationships(RELATIONSHIP_BLOCKED).values('user__id', 'user__username', 'user__first_name',
                                                                    'user__last_name',
                                                                    'user__profile__backImage',
                                                                   'user__profile__pk').order_by('id')

    def is_blocked(self, profile):
        try:
            if Relationship.objects.get(from_person=self, to_person=profile, status=RELATIONSHIP_BLOCKED):
                return True
            else:
                return False
        except ObjectDoesNotExist:
            return False

    # methods likes
    def add_like(self, profile):
        like, created = LikeProfile.objects.get_or_create(from_like=self, to_like=profile)
        return like

    def remove_like(self, profile):
        LikeProfile.objects.filter(from_like=self, to_like=profile).delete()

    def get_likes(self):
        return self.likeprofiles.filter(to_likeprofile__from_like=self)

    def has_like(self, profile):
        return LikeProfile.objects.get(from_like=self, to_like=profile)

    # methods following

    def is_follow(self, profile):
        try:
            if Relationship.objects.get(from_person=self, to_person=profile, status=RELATIONSHIP_FOLLOWING):
                return True
            else:
                return False
        except ObjectDoesNotExist:
            return False

    # Add following
    def add_follow(self, profile):
        """
        Añade una relacion de "seguido"
        :param profile perfil del usuario que se quiere seguir:
        :return a follow relation:
        """
        print('>>>>>> add_follow')
        return self.add_relationship(profile, RELATIONSHIP_FOLLOWING,
                                     False)

    def get_follow_top12(self):
        return self.relationships.filter(to_people__status=RELATIONSHIP_FOLLOWING, to_people__from_person=self).values(
            'user__username', 'user__first_name', 'user__last_name').order_by('id')[0:12]

    def get_follow_objectlist(self):
        return self.relationships.filter(to_people__status=RELATIONSHIP_FOLLOWING, to_people__from_person=self).values(
            'user__username', 'user__first_name', 'user__last_name').order_by('id')

    def add_follow_request(self, profile, notify):
        obj, created = Request.objects.get_or_create(emitter=self, receiver=profile, status=REQUEST_FOLLOWING,
                                                     notification=notify)
        return obj

    def get_follow_request(self, profile):
        return Request.objects.get(emitter=self, receiver=profile, status=REQUEST_FOLLOWING)

    def get_received_follow_requests(self):
        return self.requestsToMe.filter(from_request__status=2, from_request__receiver=self)

    def remove_received_follow_request(self, profile):
        try:
            request = Request.objects.get(emitter=self, receiver=profile, status=REQUEST_FOLLOWING)
            request.notification.delete()  # Eliminamos la notificacion
            request.delete()
        except ObjectDoesNotExist:
            return False

    # methods followers
    def is_follower(self, profile):
        try:
            if Relationship.objects.get(from_person=self, to_person=profile, status=RELATIONSHIP_FOLLOWER):
                return True
            else:
                return False
        except ObjectDoesNotExist:
            return False

    # add follower
    def add_follower(self, profile):
        print('>>>>> add_follower')
        return self.add_relationship(profile, RELATIONSHIP_FOLLOWER,
                                     False)

    def add_direct_relationship(self, profile):
        """
        Añade una relacion directamente, sin necesidad de enviar
        peticion de seguimiento.
        :param profile:
        :return True -> relacion creada con exito, False -> creacion de relación fallida:
        """
        try:
            created_follower = profile.add_follower(self)
        except ObjectDoesNotExist:
            return False
        try:
            created_follow = self.add_follow(profile)
        except ObjectDoesNotExist:
            return False

        created_follower.save()
        created_follow.save()

        t, created = timeline.models.Timeline.objects.get_or_create(author=self, profile=profile,
                                       verb='¡<a href="/profile/%s">%s</a> ahora sigue a <a href="/profile/%s">%s</a>!' % (
                                           profile.user.username,
                                           profile.user.username, self.user.username,
                                           self.user.username),
                                       type='new_relation')
        t_, created_ = timeline.models.Timeline.objects.get_or_create(author=profile, profile=self,
                                                      verb='¡<a href="/profile/%s">%s</a> tiene un nuevo seguidor, <a href="/profile/%s">%s</a>!' % (
                                                          self.user.username, self.user.username,
                                                          profile.user.username,
                                                          profile.user.username),
                                                      type='new_relation')
        if not created:
            t.save()
        if not created_:
            t.save()

        return True



    # methods friends
    '''def is_friend(self, profile):
        try:
            if Relationship.objects.get(from_person=self, to_person=profile, status=RELATIONSHIP_FRIEND):
                return True
            else:
                return False
        except ObjectDoesNotExist:
            return False'''

    '''def add_friend(self, profile):
        print('>>>>>>> add_friend')
        return self.add_relationship(profile, RELATIONSHIP_FRIEND,
                                     True)  # mas adelante cambiar aqui True por False
        # para diferenciar seguidores de seguidos.'''

    '''def get_friends_top12(self):
        return self.relationships.filter(to_people__status=RELATIONSHIP_FRIEND, to_people__from_person=self).values(
            'user__username', 'user__first_name', 'user__last_name').order_by('id')[0:12]'''

    '''def get_friends_objectlist(self):
        return self.relationships.filter(to_people__status=RELATIONSHIP_FRIEND, to_people__from_person=self).values(
            'user__username', 'user__first_name', 'user__last_name').order_by('id')'''

    '''def add_friend_request(self, profile):
        obj, created = Request.objects.get_or_create(emitter=self, receiver=profile, status=REQUEST_FRIEND)
        return obj'''

    '''def get_friend_request(self, profile):
        return Request.objects.get(emitter=self, receiver=profile, status=REQUEST_FRIEND)'''

    def get_received_friends_requests(self):
        return self.requestsToMe.filter(from_request__status=1, from_request__receiver=self)

    '''def remove_received_follow_request(self, profile):
        Request.objects.filter(emitter=profile, receiver=self, status=REQUEST_FOLLOWING).delete()'''

    """
        def get_friends_next4(self, next):
            n = next * 4
            return self.relationships.filter(to_people__status=RELATIONSHIP_FRIEND, to_people__from_person=self).order_by('id')[n-4:n]
    """

    @property
    def pin(self):
        # PIN format: pk + token + diff
        print('>>>>>>> get_pin()')
        str_pk = str(self.pk)
        length = len(str_pk)
        if length < self.PIN_LENGTH:
            diff = self.PIN_LENGTH - length - 1
            # the value used as pickle needs generate a number with 8 digits as minimal length
            pickle = 87654321.13
            if length >= 3 and length < 6:
                pickle = 876543.13
            elif length >= 6 and length < 9:
                pickle = 8765.13
            token = str(self.pk * pickle).replace('.', '')[-diff:]
            str_pk = '{}{}{}'.format(str_pk, token, diff)
            return str_pk
        else:
            return str_pk

    def get_pk_for_pin(pin):
        if len(pin) == 9:
            diff = int(pin[-1:])
            return pin[:-(diff + 1)]
        return None


User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])


class Relationship(models.Model):
    """
    Relaciones entre usuarios:
        <<from_person>> y <<to_person>>: Las dos personas que componen la relación.
        <<status>>: Estado de la relación, a escoger entre RELATIONSHIP_STATUSES
        <<created>>: Fecha de creación de la relación.
    """
    from_person = models.ForeignKey(UserProfile, related_name='from_people')
    to_person = models.ForeignKey(UserProfile, related_name='to_people')
    status = models.IntegerField(choices=RELATIONSHIP_STATUSES)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_person', 'to_person', 'status')


class LikeProfile(models.Model):
    """
    Modelo que relaciona a dos usuarios al dar "me gusta" al otro perfil.
        <<from_like>>: Persona que da like
        <<to_like>>: Persona que recibe el like
        <<created>>: Fecha de creación del like
    """
    from_like = models.ForeignKey(UserProfile, related_name='from_likeprofile')
    to_like = models.ForeignKey(UserProfile, related_name='to_likeprofile')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_like', 'to_like')


class Request(models.Model):
    """
        Modelo que gestiona las peticiones de amistad:
            <<emitter>>: Emisor de la petición
            <<receiver>>: Receptor de la petición
            <<status>>: Estado en el que se encuentra la petición
            <<created>>: Fecha en la que se creó la petición
            <<notification>>: Notificación asociada a la petición
    """
    emitter = models.ForeignKey(UserProfile, related_name='from_request')
    receiver = models.ForeignKey(UserProfile, related_name='to_request')
    status = models.IntegerField(choices=REQUEST_STATUSES)
    created = models.DateTimeField(auto_now_add=True)
    notification = models.ForeignKey(Notification, related_name='request_notification', null=True)

    class Meta:
        unique_together = ('emitter', 'receiver', 'status')
