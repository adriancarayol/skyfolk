import hashlib
import uuid
from datetime import datetime

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.http import urlencode
from taggit.managers import TaggableManager

import publications
import timeline
from notifications.models import Notification
from photologue.models import Photo

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


class UserProfileQuerySet(models.QuerySet):
    def get_all_users(self):
        return self.all()

    def get_user_by_username(self, username):
        """
        Devuelve un perfil dado un nombre de usuario
        :param: => Nombre de usuario del que se desea obtener el perfil.
        :return: Perfil asociado al nombre de usuario
        """
        return self.get(user__username=username)

    def get_last_users(self):
        """
            Devuelve la lista de perfiles ordenada
            segun su fecha de registro.
            :return: Lista ordenada por fecha de registro
        """
        return self.all().order_by('-user__date_joined')

    def get_last_login_user(self):
        """
        Devuelve el ultimo usuario que ha hecho login.
        """
        return self.all().order_by('-user__last_login')


class UserProfileManager(models.Manager):
    def get_queryset(self):
        return UserProfileQuerySet(self.model, using=self._db)

    def get_user_by_username(self, username):
        """
        Devuelve un perfil dado un nombre de usuario
        :param: => Nombre de usuario del que se desea obtener el perfil.
        :return: Perfil asociado al nombre de usuario
        """
        return self.get_queryset().get_user_by_username(username=username)

    def get_last_users(self):
        """
            Devuelve la lista de perfiles ordenada
            segun su fecha de registro.
            :return: Lista ordenada por fecha de registro
        """
        return self.all().order_by('-user__date_joined')

    def check_if_first_time_login(self, user):
        """
        Funcion para comprobar si un usuario se ha logueado
        por primera vez.
        """
        is_first_time_login = None
        user_profile = None

        try:
            user_profile = self.get(user__id=user.pk)
        except ObjectDoesNotExist:
            pass

        if user_profile:
            is_first_time_login = user_profile.is_first_login

        if is_first_time_login:
            user_profile.is_first_login = False
            user_profile.save()

        return is_first_time_login

    def get_last_login_user(self):
        """
        Devuelve el ultimo usuario que ha hecho login.
        """
        return self.get_queryset().get_last_login_user()


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
    backImage = models.ImageField(upload_to=uploadBackImagePath, verbose_name='BackImage',
                                  blank=True, null=True)
    relationships = models.ManyToManyField('self', through='Relationship', symmetrical=False, related_name='related_to')
    likeprofiles = models.ManyToManyField('self', through='LikeProfile', symmetrical=False, related_name='likesToMe')
    requests = models.ManyToManyField('self', through='Request', symmetrical=False, related_name='requestsToMe')
    timeline = models.ManyToManyField('self', through='timeline.Timeline', symmetrical=False,
                                      related_name='timeline_to')
    status = models.CharField(max_length=20, null=True, verbose_name='estado')
    ultimosUsuariosVisitados = models.ManyToManyField('self')  # Lista de ultimos usuarios visitados.
    privacity = models.CharField(max_length=4,
                                 choices=OPTIONS_PRIVACITY, default=ALL)  # Privacidad del usuario (por defecto ALL)
    is_first_login = models.BooleanField(default=True)
    tags = TaggableManager(blank=True)
    personal_pin = models.UUIDField(primary_key=False, default=uuid.uuid4, editable=False)
    objects = UserProfileManager()

    def __unicode__(self):
        return "{}'s profile".format(self.user.username)

    class Meta:
        db_table = 'user_profile'

    @property
    def group_name(self):
        """
        Devuelve el nombre del canal para enviar las notificaciones
        """
        return "users-%s" % self.pk

    @property
    def notification_channel(self):
        """
        Devuelve el nombre del canal notification para cada usuario
        """
        return "notification-%s" % self.pk

    @property
    def news_channel(self):
        """
        Devuelve el nombre del canal para enviar actualizaciones
        al tablon de inicio
        """
        return "news-%s" % self.pk

    def save(self, *args, **kwargs):
        # delete old image when replacing by updating the file
        try:
            this = UserProfile.objects.get(id=self.id)
            if this.backImage != self.backImage:
                this.backImage.delete(save=False)
        except:
            pass  # when new photo then we do nothing, normal case
        super(UserProfile, self).save(*args, **kwargs)

    # Methods of relationships between users
    def add_relationship(self, person, status, symm=False):
        """
        Añade una relación entre dos usuarios
        :param person => Persona con la que la instancia actual tiene una relacion:
        :param status => Estado de la relación:
        :param symm => Si la relación es simetrica:
        :return devuelve la relación creada:
        """
        print('>>>>>>> add_relationship')
        relationship, created = Relationship.objects.get_or_create(from_person=self, to_person=person, status=status)
        print('>>>>>>> created')
        print(created)
        if symm:
            # avoid recursion by passing 'symm=False'
            person.add_relationship(self, status, False)
        return relationship

    def remove_relationship(self, person, status, symm=False):
        """
        Elimina una relación entre dos personas
        :param person => Persona con la que la instancia actual tiene una relacion:
        :param status => Estado de la relación:
        :param symm symm => Si la relación es simetrica:
        """
        Relationship.objects.filter(from_person=self, to_person=person, status=status).delete()
        if symm:
            # avoid recursion by passing 'symm=False'
            person.remove_relationship(self, status, False)

    def get_relationships(self, status):
        """
        Devuelve las relaciones de una instancia.
        :param status => Estado de una relación:
        :return devuelve las relaciones de un perfil:
        """
        return self.relationships.filter(
            to_people__status=status,
            to_people__from_person=self)

    def get_related_to(self, status):
        """
        Conseguir relación de una persona
        :param status => Estado de la relación que se quiere conseguir:
        :return:
        """
        return self.related_to.filter(
            from_people__status=status,
            from_people__to_person=self)

    def is_visible(self, user_profile, user_pk):
        """
        Devuelve si el perfil que estamos visitando
        es visible por nosotros.
        :param user_pk, user_profile:
        :return template que determina si el perfil es visible:
        """

        # Si estoy visitando mi propio perfil
        if self.user.pk == user_pk:
            return "all"

        # Si el perfil es privado
        if self.user.pk != user_pk and \
                        self.privacity == UserProfile.NOTHING:
            return "nothing"

        # Si el perfil esta bloqueado
        if self.user.pk != user_pk and \
                self.is_blocked(user_profile):
            return "block"

        # Recuperamos la relacion de "seguidor"
        try:
            relation_follower = Relationship.objects.filter(from_person=self,
                                                            to_person=user_profile,
                                                            status=RELATIONSHIP_FOLLOWER)
        except ObjectDoesNotExist:
            relation_follower = None

        # Si el perfil es seguido y tiene la visiblidad "solo seguidores"
        if self.user.pk != user_pk and \
                        self.privacity == UserProfile.ONLYFOLLOWERS and not relation_follower:
            return "followers"

        # Recuperamos la relacion de "seguir"
        try:
            relation_follow = Relationship.objects.filter(from_person=self,
                                                          to_person=user_profile,
                                                          status=RELATIONSHIP_FOLLOWING)
        except ObjectDoesNotExist:
            relation_follow = None

        # Si la privacidad es "seguidores y/o seguidos" y cumple los requisitos
        if self.user.pk != user_pk and \
                        self.privacity == UserProfile.ONLYFOLLOWERSANDFOLLOWS and not \
                (relation_follower or relation_follow):
            return "both"

        # Si el nivel de privacidad es TODOS
        if self.privacity == UserProfile.ALL:
            return "all"
        # else...
        return None

    # Methods of timeline
    def getTimelineToMe(self):
        """
        Devuelve los objetos timeline para mi perfil (hacia mi)
        :return devuelve los objetos timeline para mi perfil:
        """
        return self.timeline_to.filter(
            from_timeline__profile=self).values('user__username', 'from_timeline__publication__content',
                                                'from_timeline__id', 'from_timeline__publication__author__username',
                                                'from_timeline__insertion_date', 'from_timeline__publication__id',
                                                'from_timeline__type', 'from_timeline__verb').order_by(
            'from_timeline__insertion_date').reverse()

    # Methods of publications (Old => Usar PublicationManager)

    def get_publication(self, publicationid):
        """
        Devuelve una publicacion a partir del identificador
        :param publicationid => Identificador de la publicación:
        :return Devuelve la publicacion solicitada:
        """
        return publications.models.Publication.objects.get(pk=publicationid)

    def remove_publication(self, publicationid):
        """
        Elimina una publicacion a partir del identificador
        :param publicationid => Identificador de la publicación:
        :return:
        """
        publications.models.Publication.objects.get(pk=publicationid).delete()

    def get_publicationsToMe(self):
        """
        Devuelve las publicaciones hacia mi perfil
        :return Devuelve las publicaciones hacia mi perfil:
        """
        return self.publications_to.filter(
            from_publication__profile=self).values('user__username', 'user__first_name', 'user__last_name',
                                                   'from_publication__id',
                                                   'from_publication__content', 'from_publication__created',
                                                   'from_publication__replies')

    def get_publicationsToMeTop15(self):
        """
        Devuelve 15 publicaciones hacia mi perfil
        :return Devuelve 15 publicaciones hacia mi perfil:
        """
        return self.publications_to.filter(
            from_publication__profile=self).values('user__username', 'user__first_name', 'user__last_name',
                                                   'from_publication__id',
                                                   'from_publication__content', 'from_publication__created')[0:15]

    def get_myPublications(self):
        """
        Devuelve las publicaciones que he realizado
        :return Devuelve las publicaciones que he realizado:
        """
        return self.publications.filter(
            to_publication__author=self).values('user__username', 'to_publication__profile', 'user__first_name',
                                                'user__last_name',
                                                'from_publication__id', 'to_publication__content',
                                                'to_publication__created', 'to_publication__user_give_me_like')

    # Obtener seguidos
    def get_following(self):
        """
        Devuelve las personas que sigo
        :return Devuelve las personas que sigo:
        """
        return self.get_relationships(RELATIONSHIP_FOLLOWING).values('user__id', 'user__username', 'user__first_name',
                                                                     'user__last_name',
                                                                     'user__profile__backImage').order_by('id')

    # Obtener seguidores
    def get_followers(self):
        """
        Devuelve las personas que son seguidores
        :return Devuelve las personas que son seguidores:
        """
        return self.get_relationships(RELATIONSHIP_FOLLOWER).values('user__id', 'user__username', 'user__first_name',
                                                                    'user__last_name',
                                                                    'user__profile__backImage').order_by('id')


    # Obtener canal de noticias de mis seguidores
    def get_all_follower_values(self):
        """
        Devuelve el canal de noticias de mis seguidores
        """
        return self.get_relationships(RELATIONSHIP_FOLLOWER)

    # methods blocks
    def add_block(self, profile):
        """
        Añade un perfil a la lista de bloqueados
        :param profile => Perfil que se desea bloquear:
        :return Devuelve la relación de bloqueado con el perfil pasado como paramatro:
        """
        return self.add_relationship(profile, RELATIONSHIP_BLOCKED,
                                     False)

    def get_blockeds(self):
        """
        Devuelve la lista de bloqueados del perfil instanciado
        :return Devuelve la lista de bloqueados del perfil instanciado:
        """
        return self.get_relationships(RELATIONSHIP_BLOCKED).values('user__id', 'user__username', 'user__first_name',
                                                                   'user__last_name',
                                                                   'user__profile__backImage',
                                                                   'user__profile__pk').order_by('id')

    def is_blocked(self, profile):
        """
        Método para comprobar si un perfil está bloqueado
        :param profile => Perfil que quizás este bloqueado:
        :return Devuelve un booleano dependiendo de si está o no
        bloqueado el perfil pasado como paramatro:
        """
        try:
            if Relationship.objects.get(from_person=self, to_person=profile, status=RELATIONSHIP_BLOCKED):
                return True
            else:
                return False
        except ObjectDoesNotExist:
            return False

    # methods likes
    def add_like(self, profile):
        """
        Añade un "me gusta" a un perfil
        :param profile => Perfil que doy "me gusta":
        :return Devuelve la relación "Me gusta":
        """
        like, created = LikeProfile.objects.get_or_create(from_like=self, to_like=profile)
        return like

    def remove_like(self, profile):
        """
        Elimina la relación "me gusta"
        :param profile => Perfil al que quiero quitar mi "me gusta":
        """
        LikeProfile.objects.filter(from_like=self, to_like=profile).delete()

    def get_likes(self):
        """
        Obtengo los likes que ha dado del perfil instanciado
        :return Devuelve los likes del perfil instanciado:
        """
        return self.likeprofiles.filter(to_likeprofile__from_like=self)

    def get_likes_to_me(self):
        """
        Obtengo los likes que me han dado.
        :return: Devuelve los likes recibidos
        """
        return LikeProfile.objects.get_all_likes_to_me(self)

    def has_like(self, profile):
        """
        Comprueba si un perfil tiene un "me gusta" del perfil instanciado
        :param profile => Perfil que se comprueba si tiene un me gusta del perfil instanciado:
        """
        return LikeProfile.objects.get(from_like=self, to_like=profile)

    # methods following

    def is_follow(self, profile):
        """
        Comprueba si sigo al perfil pasado como parametro
        :param profile => Perfil que se comprueba si lo sigo:
        :return Booleano dependiendo de si sigo al perfil o no:
        """
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
        """
        Devuelve 12 seguidos ordenados por ID
        :return Devuelve 12 seguidos ordenados por ID:
        """
        return self.relationships.filter(to_people__status=RELATIONSHIP_FOLLOWING, to_people__from_person=self).values(
            'user__username', 'user__first_name', 'user__last_name').order_by('id')[0:12]

    def get_follow_objectlist(self):
        """
        Devuelve la lista de seguidos por un perfil
        :return Devuelve la lista de seguidos por un perfil:
        """
        return self.relationships.filter(to_people__status=RELATIONSHIP_FOLLOWING, to_people__from_person=self).values(
            'user__username', 'user__first_name', 'user__last_name').order_by('id')

    def add_follow_request(self, profile, notify):
        """
        Añade una solicitud de seguimiento
        :param profile => Perfil que quiero seguir:
        :param notify => Notificacion generada:
        """
        obj, created = Request.objects.get_or_create(emitter=self, receiver=profile, status=REQUEST_FOLLOWING)
        # Si existe la peticion de amistad, actualizamos la notificacion
        obj.notification = notify
        obj.save()
        return obj

    def get_follow_request(self, profile):
        """
        Devuelve la petición de seguimiento de un perfil
        :param profile => Perfil del que se quiere recuperar la solicitud de seguimiento:
        :return Devuelve la petición de seguimiento de un perfil:
        """
        return Request.objects.get(emitter=self, receiver=profile, status=REQUEST_FOLLOWING)

    def get_received_follow_requests(self):
        """
        Devuelve las peticiones de segumiento para mi perfil (perfil instanciado)
        :return Devuelve las peticiones de segumiento para mi perfil:
        """
        return self.requestsToMe.filter(from_request__status=2, from_request__receiver=self)

    def remove_received_follow_request(self, profile):
        """
        Elimina la petición de seguimiento hacia un perfil
        :param profile => Perfil del que se quiere eliminar una petición de seguimiento:
        """
        try:
            request = Request.objects.get(emitter=self, receiver=profile, status=REQUEST_FOLLOWING)
            request.notification.delete()  # Eliminamos la notificacion
            request.delete()
        except ObjectDoesNotExist:
            return False

    # methods followers
    def is_follower(self, profile):
        """
        Comprueba si el perfil pasado como parametro es un seguidor mio
        :param profile => Perfil del que quiero comprobar si es un seguidor:
        :return Booleano que indica si es seguidor o no:
        """
        try:
            if Relationship.objects.get(from_person=self, to_person=profile, status=RELATIONSHIP_FOLLOWER):
                return True
            else:
                return False
        except ObjectDoesNotExist:
            return False

    # add follower
    def add_follower(self, profile):
        """
        El perfil pasado como parametro se añade como seguidor del perfil instancia
        :param profile => Perfil que se quiere añadie a la lista de seguidores:
        :return => Relación de seguidor:
        """
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

        # Creamos historia en el perfil del usuario que seguimos
        t, created = timeline.models.Timeline.objects.get_or_create(author=self, profile=profile,
                                                                    verb='¡<a href="/profile/%s">%s</a> tiene un nuevo seguidor, <a href="/profile/%s">%s</a>!' % (
                                                                        profile.user.username,
                                                                        profile.user.username,
                                                                        self.user.username,
                                                                        self.user.username),
                                                                    type='new_relation')
        # Creamos historia en nuestro perfil
        t2, created2 = timeline.models.Timeline.objects.get_or_create(author=profile, profile=self,
                                                                      verb='¡<a href="/profile/%s">%s</a> ahora sigue a <a href="/profile/%s">%s</a>!' % (
                                                                          self.user.username,
                                                                          self.user.username,
                                                                          profile.user.username,
                                                                          profile.user.username),
                                                                      type='new_relation')
        # Actualizamos fecha en el timeline
        if not created:
            t.insertion_date = datetime.now()
            t.save()
        # Actualizamos fecha en el timeline
        if not created2:
            t2.insertion_date = datetime.now()
            t2.save()

        return True

    # Funcion despreciable
    def get_received_friends_requests(self):
        return self.requestsToMe.filter(from_request__status=1, from_request__receiver=self)

    # Methods of multimedia
    def get_num_multimedia(self):
        """
        Devuelve el numero de contenido multimedia de un perfil.
        """
        return Photo.objects.filter(owner=self.user).count()

    @property
    def gravatar(self, size=120):
        """
        Devuelve el gravatar por defecto asociado al email
        del usuario
        :param size => tamaño de la imagen:
        :return url con el gravatar del usuario, o la imagen por defecto de skyfolk:
        """
        default = 'http://pre.skyfolk.net/static/img/nuevo.png'
        return "https://www.gravatar.com/avatar/%s?%s" % (
            hashlib.md5(str(self.user.email.lower()).encode('utf-8')).hexdigest(),
            urlencode({'d': default, 's': str(size).encode('utf-8')}))


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


class LikeProfileQuerySet(models.QuerySet):
    """
        Query Manager para usuarios favoritos
    """

    def get_all_likes(self, from_like):
        """
        Devuelve todos los me gusta dados por un perfil en concreto.
        :param from_like => Del perfil que da me gusta:
        :return Todos los me gusta dados por un perfil en concreto:
        """
        return self.filter(from_like=from_like)

    def get_last_like(self, from_like):
        """
        Devuelve el ultimo me gusta dado por un perfil
        :param from_like => Perfil que da me gusta:
        :return El ultimo me gusta dado por un perfil:
        """
        return self.filter(from_like=from_like).latest()

    def get_likes_by_created(self, from_like, reverse=True):
        """
        Devuelve los me gusta dados por un perfil
        ordenados por la creacion
        :param from_like => Perfil emisor:
        :param reverse => Perfil receptor:
        :return  me gusta dados por un perfil ordenados por la creacion:
        """
        if reverse:
            return self.filter(from_like=from_like).order_by('-created')
        return self.filter(from_like=from_like).order_by('created')

    def get_all_likes_to_me(self, to_like):
        """
        Devuelve la lista de usuarios
        que me han dado me gusta.
        """
        return self.filter(to_like=to_like)


class LikeProfileManager(models.Manager):
    """
        Manager para usuarios que me gustan
    """

    def get_queryset(self):
        return LikeProfileQuerySet(self.model, using=self._db)

    def get_all_likes(self, from_like):
        """
        Devuelve todos los me gusta dados por un perfil en concreto.
        :param from_like => Del perfil que da me gusta:
        :return Todos los me gusta dados por un perfil en concreto:
        """
        return self.get_queryset().get_all_likes(from_like=from_like)

    def get_last_like(self, from_like):
        """
        Devuelve el ultimo me gusta dado por un perfil
        :param from_like => Perfil que da me gusta:
        :return El ultimo me gusta dado por un perfil:
        """
        return self.get_queryset().get_last_like(from_like=from_like)

    def get_likes_by_created(self, from_like, reverse=False):
        """
        Devuelve los me gusta dados por un perfil
        ordenados por la creacion
        :param from_like => Perfil emisor:
        :param reverse => Perfil receptor:
        :return  me gusta dados por un perfil ordenados por la creacion:
        """
        return self.get_queryset().get_likes_by_created(from_like=from_like, reverse=reverse)

    def get_all_likes_to_me(self, to_like):
        """
        Devuelve la lista de usuarios
        que me han dado me gusta.
        """
        return self.get_queryset().get_all_likes_to_me(to_like=to_like)


class LikeProfile(models.Model):
    """
    Modelo que relaciona a dos usuarios al dar "me gusta" al otro perfil.
        <<from_like>>: Persona que da like
        <<to_like>>: Persona que recibe el like
        <<created>>: Fecha de creación del like
    """

    class Meta:
        get_latest_by = 'created'
        unique_together = ('from_like', 'to_like')

    from_like = models.ForeignKey(UserProfile, related_name='from_likeprofile')
    to_like = models.ForeignKey(UserProfile, related_name='to_likeprofile')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Emitter: {0} Receiver: {1} Created: {2}".format(self.from_like.user.username,
                                                                self.to_like.user.username, self.created)

    objects = LikeProfileManager()


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


class AffinityUserManager(models.Manager):
    """
        Manager para ultimos usuarios visitados por afinidad/tiempo
    """

    def get_all_relations(self, emitterid):
        """
        Devuelve todas las relaciones <<ultimos usuarios visitados>>
        :param emitterid => Emisor de la relacion:
        :return relaciones del emisor:
        """
        return self.filter(emitter=emitterid)

    def get_relation(self, emitterid, receiver):
        """
        Devuelve la relacion creada entre dos perfiles
        :param emitterid => Perfil emisor:
        :param receiver => Perfil receptor:
        :return relacion entre emisor/receptor:
        """
        return self.filter(emitter=emitterid, receiver=receiver)

    def get_affinity(self, emitterid, receiver):
        """
        Devuelve la afinidad entre dos perfiles
        :param emitterid => Perfil emisor:
        :param receiver => Perfil receptor:
        :return afinidad entre dos usuarios:
        """
        return self.get(emitter=emitterid, receiver=receiver)

    def get_relations_by_created(self, emitterid, reverse=True):
        """
        Devuelve relaciones ordenadas por la creacion
        :param emitterid => Perfil emisor:
        :param reverse => Perfil receptor:
        :return relaciones ordenadas segun la creacion:
        """
        if reverse:
            return self.filter(emitter=emitterid).order_by('-created')

        return self.filter(emitter=emitterid).order_by('created')

    def get_last_relation(self, emitterid):
        """
        Devuelve la ultima relacion creada
        :param emitterid => Perfil emisor:
        :return ultima relacion creada:
        """
        return self.filter(emitter=emitterid).latest()

    def get_favourite_relation(self, emitterid):
        """
        Devuelve la relacion favorita (por afinidad)
        :param emitterid => Perfil emisor:
        :return devuelve relaciones de mayor a menor afinidad:
        """
        return self.filter(emitter=emitterid).order_by('-affinity')

    def check_limit(self, emitterid):
        """
        Comprueba el limite de usuarios en la lista de favoritos
        Si alcanza el limite, elimina el que menos afinidad/fecha de creacion
        tenga.
        """
        LIMIT_USERS = 6
        if self.filter(emitter=emitterid).count() > LIMIT_USERS:
            print('>> HAVE: {} relations.'.format(self.count()))
            try:
                candidate = self.filter(emitter=emitterid).order_by('created', 'affinity')[0]
            except ObjectDoesNotExist:
                candidate = None
            if candidate:
                print('Borrando candidato: {}'.format(candidate.receiver.user.username))
                candidate.delete()


class AffinityUser(models.Model):
    """
        Modelo para gestionar los últimos usuarios visitados
        cada usuario visitado tendra una afinidad,
        esta se incrementara tantas veces como se visite un perfil
        o actuemos con objetos de ese perfil(dar me gusta a comentarios,
        añadir a mi timeline algun comentario suyo...
    """

    class Meta:
        get_latest_by = 'created'
        unique_together = ('emitter', 'receiver')

    emitter = models.ForeignKey(UserProfile, related_name='from_profile_affinity')
    receiver = models.ForeignKey(UserProfile, related_name='to_profile_affinity')
    affinity = models.IntegerField(verbose_name='affinity', default=0)
    created = models.DateTimeField(auto_now_add=True)
    objects = AffinityUserManager()

    def __str__(self):
        return "Emitter: {0} Receiver: {1} Created: {2}".format(self.emitter.user.username, self.receiver.user.username,
                                                                self.created)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, increment=True):
        """
            Autoincrementar afinidad
        """
        if increment:
            self.affinity += 1
        self.created = datetime.now()
        super(AffinityUser, self).save()


class AuthDevicesQuerySet(models.QuerySet):
    """
        Query Manager para Auth Devices
    """

    def get_auth_device(self, user, token):
        """
        Devuelve el objeto device relacionando usuario con dispositivos a los que se conecta a skyfolk.
        :param Usuario del que se quiere obtener los dispositivos que usa:
        :return Devuelve el objeto device relacionando usuario con dispositivos a los que se conecta a skyfolk.:
        """
        return self.filter(user_profile=user, browser_token=token)

    def get_devices_by_user(self, user):
        """
        Devuelve todos los navegadores usados por un usuario.
        :param user:
        :return Devuelve los navegadores usados por un usuario:
        """
        return self.filter(user_profile=user)


class AuthDevicesManager(models.Manager):
    """
        Manager para Auth Devices
    """

    def get_queryset(self):
        return AuthDevicesQuerySet(self.model, using=self._db)

    def get_device(self, user, token):
        """
        Devuelve el objeto device relacionando usuario con dispositivos a los que se conecta a skyfolk.
        :param Usuario del que se quiere obtener los dispositivos que usa:
        :return Devuelve el objeto device relacionando usuario con dispositivos a los que se conecta a skyfolk.:
        """
        return self.get_queryset().get_auth_device(user=user, token=token)

    def get_devices_by_user(self, user):
        """
        Devuelve todos los navegadores usados por un usuario.
        :param user:
        :return Devuelve los navegadores usados por un usuario:
        """
        return self.get_queryset().get_devices_by_user(user=user)


class AuthDevices(models.Model):
    """
        Establece una relacion entre el usuario y los navegadores/dispositivos que usa.
    """
    user_profile = models.ForeignKey(UserProfile, related_name='device_to_profile')
    browser_token = models.CharField(max_length=1024)
    objects = AuthDevicesManager()
