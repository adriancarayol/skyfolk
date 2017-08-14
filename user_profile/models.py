import hashlib
import datetime
import os, glob

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.http import urlencode
from notifications.models import Notification
from photologue.models import Photo
from django_neomodel import DjangoNode
from neomodel import UniqueIdProperty, Relationship, StringProperty, RelationshipTo, RelationshipFrom, IntegerProperty, \
    BooleanProperty, Property, StructuredRel, DateTimeProperty
from django.core.cache import cache
from neomodel.properties import validator
from django.utils.translation import ugettext_lazy as _
from django.core.files.storage import FileSystemStorage

REQUEST_FOLLOWING = 1
REQUEST_FOLLOWER = 2
REQUEST_BLOCKED = 3
REQUEST_STATUSES = (
    (REQUEST_FOLLOWING, 'Following'),
    (REQUEST_FOLLOWER, 'Follower'),
    (REQUEST_BLOCKED, 'Blocked'),
)


def upload_cover_path(instance, filename):
    return '%s/cover_image/%s' % (instance.user.username, filename)


class Profile(models.Model):
    """
    Modelo para guardar
    informacion extra del usuario
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    back_image = models.ImageField(blank=True, null=True, upload_to=upload_cover_path)
    status = models.CharField(blank=True, null=True, max_length=100)
    is_first_login = models.BooleanField(default=True)

    def last_seen(self):
        return cache.get('seen_%s' % self.user.username)

    def online(self):
        if self.last_seen():
            now = datetime.datetime.now()
            if now > self.last_seen() + datetime.timedelta(seconds=settings.USER_ONLINE_TIMEOUT):
                return False
            else:
                return True
        else:
            return False

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
            hashlib.md5(str(User.objects.get(id=self.user_id).email).encode('utf-8')).hexdigest(),
            urlencode({'d': default, 's': str(size).encode('utf-8')}))

    def check_if_first_time_login(self):
        """
        Funcion para comprobar si un usuario se ha logueado
        por primera vez.
        """
        is_first_time_login = self.is_first_login

        if is_first_time_login:
            self.is_first_login = False
            self.save()

        return is_first_time_login


    # Methods of multimedia
    def get_num_multimedia(self):
        """
        Devuelve el numero de contenido multimedia de un perfil (sin imagenes privadas).
        """
        return Photo.objects.filter(owner=self.user_id, is_public=True).count()

    def get_total_num_multimedia(self):
        """
        Devuelve el numero de contenido multimedia de un perfil.
        """
        return Photo.objects.filter(owner=self.user_id).count()


class TagProfile(DjangoNode):
    uid = UniqueIdProperty()
    title = StringProperty(unique_index=True)
    common = Relationship('TagProfile', 'COMMON')
    user = RelationshipFrom('NodeProfile', 'INTEREST')

    class Meta:
        app_label = 'tag_profile'


class UploadedFileProperty(Property):
    def __init__(self, **kwargs):
        for item in ['required', 'unique_index', 'index', 'default']:
            if item in kwargs:
                raise ValueError('{} argument ignored by {}'.format(item, self.__class__.__name__))

        # kwargs['unique_index'] = True
        super(UploadedFileProperty, self).__init__(**kwargs)

    @validator
    def inflate(self, value):
        return str(value)

    @validator
    def deflate(self, value):
        return str(value)


class FollowRel(StructuredRel):
    weight = IntegerProperty(default=0)
    created = DateTimeProperty(default=lambda: datetime.datetime.now())

    class Meta:
        app_label = 'django_rel'


class NodeProfile(DjangoNode):
    uid = UniqueIdProperty() #TODO: Eliminar este field
    user_id = IntegerProperty(unique_index=True)  # user_id
    title = StringProperty(unique_index=True)  # username
    follow = RelationshipTo('NodeProfile', 'FOLLOW', model=FollowRel)  # follow user
    like = RelationshipTo('NodeProfile', 'LIKE')  # like user
    bloq = RelationshipTo('NodeProfile', 'BLOQ')  # bloq user
    is_active = BooleanProperty(default=True, help_text=_(
        'Designates whether this user should be treated as active. '
        'Unselect this instead of deleting accounts.'))

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
    privacity = StringProperty(choices=OPTIONS_PRIVACITY, default='A')

    @property
    def group_name(self):
        """
        Devuelve el nombre del canal para enviar las notificaciones
        """
        return "users-%s" % self.user_id

    @property
    def notification_channel(self):
        """
        Devuelve el nombre del canal notification para cada usuario
        """
        return "notification-%s" % self.user_id

    @property
    def news_channel(self):
        """
        Devuelve el nombre del canal para enviar actualizaciones
        al tablon de inicio
        """
        return "news-%s" % self.user_id

    class Meta:
        app_label = 'node_profile'

    def get_followers(self):
        results, columns = self.cypher("MATCH (a)<-[:FOLLOW]-(b) WHERE id(a)={self} AND b.is_active=true RETURN b")
        return [self.inflate(row[0]) for row in results]

    def count_followers(self):
        results, columns = self.cypher(
            "MATCH (a)<-[:FOLLOW]-(b) WHERE id(a)={self} and b.is_active=true RETURN COUNT(b)")
        return results[0][0]

    def get_follows(self):
        results, columns = self.cypher("MATCH (a)-[:FOLLOW]->(b) WHERE id(a)={self} AND b.is_active=true RETURN b")
        return [self.inflate(row[0]) for row in results]

    def count_follows(self):
        results, columns = self.cypher(
            "MATCH (a)-[:FOLLOW]->(b) WHERE id(a)={self} and b.is_active=true RETURN COUNT(b)")
        return results[0][0]

    def has_like(self, to_like):
        results, columns = self.cypher(
            "MATCH (a)-[like:LIKE]->(b) WHERE id(a)={self} AND b.user_id=%d RETURN like" % to_like)
        return True if len(results) > 0 else False

    def count_likes(self):
        results, columns = self.cypher(
            "MATCH (n:NodeProfile)<-[like:LIKE]-(m:NodeProfile) WHERE id(n)={self} RETURN COUNT(like)")
        return results[0][0]

    def get_like_to_me(self):
        results, columns = self.cypher(
            "MATCH (n:NodeProfile)<-[like:LIKE]-(m:NodeProfile) WHERE id(n)={self} RETURN m")
        return [self.inflate(row[0]) for row in results]

    def get_favs_users(self):
        results, columns = self.cypher(
            "MATCH (a)-[follow:FOLLOW]->(b) WHERE id(a)={self} and b.is_active=true RETURN b ORDER BY follow.weight DESC LIMIT 6")
        return [self.inflate(row[0]) for row in results]

    def is_visible(self, user_profile):
        """
        Devuelve si el perfil con id user_id
        es visible por nosotros.
        :param user_id:
        :return template que determina si el perfil es visible:
        """

        # Si estoy visitando mi propio perfil
        if self.user_id == user_profile.user_id:
            return "all"

        # Si el perfil es privado
        if self.privacity == NodeProfile.NOTHING:
            return "nothing"

        # Si el perfil esta bloqueado
        if self.bloq.is_connected(user_profile):
            return "block"

        # Recuperamos la relacion de "seguidor"
        try:
            relation_follower = user_profile.follow.is_connected(self)
        except ObjectDoesNotExist:
            relation_follower = None

        # Si el perfil es seguido y tiene la visiblidad "solo seguidores"
        if self.privacity == NodeProfile.ONLYFOLLOWERS and not relation_follower:
            return "followers"

        # Recuperamos la relacion de "seguir"
        try:
            relation_follow = self.follow.is_connected(user_profile)
        except ObjectDoesNotExist:
            relation_follow = None

        # Si la privacidad es "seguidores y/o seguidos" y cumple los requisitos
        if self.privacity == NodeProfile.ONLYFOLLOWERSANDFOLLOWS and not \
                (relation_follower or relation_follow):
            return "both"

        # Si el nivel de privacidad es TODOS
        if self.privacity == NodeProfile.ALL:
            return "all"

        return None



class RequestManager(models.Manager):
    def get_follow_request(self, from_profile, to_profile):
        """
        Devuelve la petición de seguimiento de un perfil
        :param profile => Perfil del que se quiere recuperar la solicitud de seguimiento:
        :return Devuelve la petición de seguimiento de un perfil:
        """
        return self.get(emitter_id=from_profile,
                        receiver_id=to_profile, status=REQUEST_FOLLOWING)

    def add_follow_request(self, from_profile, to_profile, notify):
        """
        Añade una solicitud de seguimiento
        :param profile => Perfil que quiero seguir:
        :param notify => Notificacion generada:
        """
        obj, created = self.get_or_create(emitter_id=from_profile,
                                          receiver_id=to_profile,
                                          status=REQUEST_FOLLOWING)
        # Si existe la peticion de amistad, actualizamos la notificacion
        obj.notification = notify
        obj.save()
        return obj

    def remove_received_follow_request(self, from_profile, to_profile):
        """
        Elimina la petición de seguimiento hacia un perfil
        :param profile => Perfil del que se quiere eliminar una petición de seguimiento:
        """
        try:
            request = Request.objects.get(emitter_id=from_profile, receiver_id=to_profile, status=REQUEST_FOLLOWING)
            request.notification.delete()  # Eliminamos la notificacion
            request.delete()
            return True
        except ObjectDoesNotExist:
            return False


class Request(models.Model):
    """
        Modelo que gestiona las peticiones de amistad:
            <<emitter>>: Emisor de la petición
            <<receiver>>: Receptor de la petición
            <<status>>: Estado en el que se encuentra la petición
            <<created>>: Fecha en la que se creó la petición
            <<notification>>: Notificación asociada a la petición
    """
    emitter = models.ForeignKey(User, related_name='from_request')
    receiver = models.ForeignKey(User, related_name='to_request')
    status = models.IntegerField(choices=REQUEST_STATUSES)
    created = models.DateTimeField(auto_now_add=True)
    notification = models.ForeignKey(Notification, related_name='request_notification', null=True)
    objects = RequestManager()

    class Meta:
        unique_together = ('emitter', 'receiver', 'status')


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
    user_profile = models.ForeignKey(User, related_name='device_to_profile')
    browser_token = models.CharField(max_length=1024)
    objects = AuthDevicesManager()
