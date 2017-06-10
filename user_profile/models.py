import hashlib
import uuid
import datetime
import io

from skyfolk import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.http import urlencode
from notifications.models import Notification
from photologue.models import Photo
from django_neomodel import DjangoNode
from neomodel import UniqueIdProperty, Relationship, StringProperty, RelationshipTo, RelationshipFrom, IntegerProperty, BooleanProperty, Property
from django.core.cache import cache
from neomodel.properties import validator
from depot.manager import DepotManager
from depot.io.utils import FileIntent

REQUEST_FOLLOWING = 1
REQUEST_FOLLOWER = 2
REQUEST_BLOCKED = 3
REQUEST_STATUSES = (
    (REQUEST_FOLLOWING, 'Following'),
    (REQUEST_FOLLOWER, 'Follower'),
    (REQUEST_BLOCKED, 'Blocked'),
)

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

    def get_last_login_user(self):
        """
        Devuelve el ultimo usuario que ha hecho login.
        """
        return self.get_queryset().get_last_login_user()


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
        uuid.UUID(value)
        return value

    @validator
    def deflate(self, value):
        uuid.UUID(value)
        return value

class NodeProfile(DjangoNode):
    uid = UniqueIdProperty()
    user_id = IntegerProperty(unique_index=True)  # user_id
    title = StringProperty(unique_index=True)  # username
    first_name = StringProperty(unique_index=True) # first_name
    last_name = StringProperty(unique_index=True) # last_name
    follow = RelationshipTo('NodeProfile', 'FOLLOW')  # follow user
    like = RelationshipTo('NodeProfile', 'LIKE')  # like user
    bloq = RelationshipTo('NodeProfile', 'BLOQ')  # bloq user
    is_first_login = BooleanProperty(default=True)
    status = StringProperty(required=False)
    back_image_ = UploadedFileProperty(db_property='back_image')

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
    def back_image(self):
        depot = DepotManager.get()
        return depot.get(self.back_image_)

    @back_image.setter
    def back_image(self, value):
        depot = DepotManager.get()

        if self.back_image_:
            depot.delete(self.back_image_)
            self.back_image_ = None

        # set the value
        if isinstance(value, str):
            try:
                uuid.UUID(value)
                self.back_image_ = uuid.UUID(value)
            except ValueError:
                raise TypeError('Value "{}" is not a uuid'.format(value))
        elif isinstance(value, (FileIntent, io.IOBase)):
            self.back_image_ = depot.create(value)
        else:
            TypeError('Value "{}" should be of type file or FileIntent'.format(value))

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
        results, columns = self.cypher("MATCH (a) WHERE id(a)={self} MATCH (a)<-[:FOLLOW]-(b) RETURN b")
        return [self.inflate(row[0]) for row in results]

    def count_followers(self):
        results, columns = self.cypher("MATCH (a) WHERE id(a)={self} MATCH (a)<-[:FOLLOW]-(b) RETURN COUNT(b)")
        return results[0][0]

    def get_follows(self):
        results, columns = self.cypher("MATCH (a) WHERE id(a)={self} MATCH (a)-[:FOLLOW]->(b) RETURN b")
        return [self.inflate(row[0]) for row in results]

    def count_follows(self):
        results, columns = self.cypher("MATCH (a) WHERE id(a)={self} MATCH (a)-[:FOLLOW]->(b) RETURN COUNT(b)")
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


class UserProfile(models.Model):
    """
    Diferentes opciones de privacidad para el usuario
    """
    user = models.OneToOneField(User, related_name='profile')
    backImage = models.ImageField(upload_to=uploadBackImagePath, verbose_name='BackImage',
                                  blank=True, null=True)
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

    def last_seen(self):
        return cache.get('seen_%s' % self.user.username)

    def online(self):
        if self.last_seen():
            now = datetime.datetime.now()
            if now > self.last_seen() + datetime.timedelta(seconds=settings.base.USER_ONLINE_TIMEOUT):
                return False
            else:
                return True
        else:
            return False


# User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])

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

    emitter = models.ForeignKey(User, related_name='from_profile_affinity')
    receiver = models.ForeignKey(User, related_name='to_profile_affinity')
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
        self.created = datetime.datetime.now()
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
    user_profile = models.ForeignKey(User, related_name='device_to_profile')
    browser_token = models.CharField(max_length=1024)
    objects = AuthDevicesManager()
