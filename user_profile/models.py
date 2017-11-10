import datetime
import hashlib
import logging

from badgify.models import Award, Badge
from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import models
from django.db import transaction
from django.utils.http import urlencode

from notifications.models import Notification
from photologue.models import Photo, Video

REQUEST_FOLLOWING = 1
REQUEST_BLOCKED = 3
REQUEST_STATUSES = (
    (REQUEST_FOLLOWING, 'Following'),
    (REQUEST_BLOCKED, 'Blocked'),
)

FOLLOWING = 1
BLOCK = 3
RELATIONSHIP_STATUSES = (
    (FOLLOWING, 1),
    (BLOCK, 3)
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def upload_cover_path(instance, filename):
    return '%s/cover_image/%s' % (instance.user.username, filename)


class RelationShipProfile(models.Model):
    """
    Establece una relacion entre dos usuarios
    """
    to_profile = models.ForeignKey('Profile', related_name='to_profile', db_index=True)
    from_profile = models.ForeignKey('Profile', related_name='from_profile', db_index=True)
    type = models.IntegerField(choices=RELATIONSHIP_STATUSES)

    class Meta:
        unique_together = ('to_profile', 'from_profile')


class Profile(models.Model):
    """
    Modelo para guardar
    informacion extra del usuario
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    back_image = models.ImageField(blank=True, null=True, upload_to=upload_cover_path)
    status = models.CharField(blank=True, null=True, max_length=100)
    is_first_login = models.BooleanField(default=True)
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
    privacity = models.CharField(choices=OPTIONS_PRIVACITY, default='A', max_length=4)
    relationships = models.ManyToManyField('self', through=RelationShipProfile, symmetrical=False,
                                           related_name="profile_relationships")

    reindex_related = ('user',)

    class Meta:
        ordering = ['-user__date_joined']

    def __str__(self):
        return "%s profile" % self.user.username

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
        :param size: Size of avatar
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
            try:
                with transaction.atomic(using='default'):
                    self.is_first_login = False
                    Award.objects.create(user=self.user, badge=Badge.objects.get(slug='new-account'))
                    self.save()
            except Exception as e:
                logger.info(e)

        return is_first_time_login

    # Methods of multimedia
    def get_num_multimedia(self):
        """
        Devuelve el numero de contenido multimedia de un perfil (sin imagenes privadas).
        """
        return Photo.objects.filter(owner=self.user_id, is_public=True).count() + Video.objects.filter(
            owner=self.user_id, is_public=True).count()

    def get_total_num_multimedia(self):
        """
        Devuelve el numero de contenido multimedia de un perfil.
        """
        return Photo.objects.filter(owner=self.user_id).count() + Video.objects.filter(owner=self.user_id).count()

    def is_visible(self, user_profile):
        """
        Devuelve si el perfil con id user_id
        es visible por nosotros.
        :param user_profile:
        :return devuelve el nivel de visibilidad:
        """

        # Si estoy visitando mi propio perfil
        if self.id == user_profile.id:
            return "all"

        # Si el perfil es privado
        if self.privacity == Profile.NOTHING:
            return "nothing"

        # Si el perfil me bloquea
        if RelationShipProfile.objects.filter(to_profile=user_profile, from_profile=self, type=BLOCK).exists():
            return "block"

        # Recuperamos la relacion de "seguidor"
        try:
            relation_follower = RelationShipProfile.objects.filter(to_profile=self, from_profile=user_profile,
                                                                   type=FOLLOWING)
        except Exception:
            relation_follower = None

        # Si el perfil es seguido y tiene la visiblidad "solo seguidores"
        if self.privacity == Profile.ONLYFOLLOWERS and not relation_follower:
            return "followers"

        # Recuperamos la relacion de "seguir"
        try:
            relation_follow = RelationShipProfile.objects.filter(to_profile=user_profile, from_profile=self,
                                                                 type=FOLLOWING)
        except Exception:
            relation_follow = None

        # Si la privacidad es "seguidores y/o seguidos" y cumple los requisitos
        if self.privacity == Profile.ONLYFOLLOWERSANDFOLLOWS and not \
                (relation_follower or relation_follow):
            return "both"

        # Si el nivel de privacidad es TODOS
        if self.privacity == Profile.ALL:
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
        request = Request.objects.get(emitter_id=from_profile, receiver_id=to_profile, status=REQUEST_FOLLOWING)
        request.notification.delete()  # Eliminamos la notificacion
        request.delete()


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


class NotificationSettings(models.Model):
    """
    Permite al usuario establecer que tipo de notificaciones quiere recibir
    """
    email_when_new_notification = models.BooleanField(default=True)
    email_when_recommendations = models.BooleanField(default=True)
    email_when_mp = models.BooleanField(default=True)
    followed_notifications = models.BooleanField(default=True)
    followers_notifications = models.BooleanField(default=True)
    only_confirmed_users = models.BooleanField(default=True)
    user = models.OneToOneField(User, related_name='notification_settings')
