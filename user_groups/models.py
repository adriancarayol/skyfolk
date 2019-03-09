# encoding:utf-8
import itertools
from django.db import IntegrityError
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.text import slugify
from taggit.managers import TaggableManager

REQUEST_FOLLOWING = 1
REQUEST_FOLLOWER = 2
REQUEST_BLOCKED = 3
REQUEST_STATUSES = (
    (REQUEST_FOLLOWING, 'Following'),
    (REQUEST_FOLLOWER, 'Follower'),
    (REQUEST_BLOCKED, 'Blocked'),
)


def upload_small_group_image(instance, filename):
    return '%s/small_group_image/%s' % (instance.name, filename)


def upload_large_group_image(instance, filename):
    return '%s/large_group_image/%s' % (instance.name, filename)


def group_avatar_path(instance, filename):
    return 'group_{0}_avatar/{1}'.format(instance.id, filename)


def group_back_image_path(instance, filename):
    return 'group_{0}_back_image/{1}'.format(instance.id, filename)


def group_themes_images(instance, filename):
    return 'group_{0}/themes/{1}'.format(instance.board_group, filename)


class UserGroups(models.Model):
    """
        Proxy para grupos.
    """
    name = models.CharField(max_length=255)
    users = models.ManyToManyField(User, related_name="user_groups")
    owner = models.ForeignKey(User, related_name='owner_group', on_delete=models.CASCADE)
    slug = models.SlugField(max_length=256, unique=True)
    description = models.CharField(max_length=500)
    is_public = models.BooleanField(default=True)
    avatar = models.ImageField(upload_to=group_avatar_path, null=True, blank=True)
    back_image = models.ImageField(upload_to=group_back_image_path, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    tags = TaggableManager(blank=True)

    class Meta:
        permissions = (
            ('view_notification', 'View notification'),
            ('can_publish', 'Can publish'),
            ('change_description', 'Change description'),
            ('delete_publication', 'Delete publication'),
            ('delete_image', 'Delete image'),
            ('kick_member', 'Kick member'),
            ('ban_member', 'Ban member'),
            ('modify_notification', 'Modify notification'),
        )

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(UserGroups, self).save(*args, **kwargs)

    @property
    def group_channel(self):
        return "group-%d" % self.id

    @property
    def get_total_multimedia(self):
        return self.group_photos.count() + self.group_videos.count()


class GroupTheme(models.Model):
    board_group = models.ForeignKey(UserGroups, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=2048)
    title = models.CharField(max_length=256)
    image = models.ImageField(upload_to=group_themes_images, blank=True, null=True)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ('-created', )

    def save(self, *args, **kwargs):
        self.slug = orig = slugify(str(self.owner_id) + self.title)
        for x in itertools.count(1):
            if not GroupTheme.objects.filter(slug=self.slug).exists():
                try:
                    super(GroupTheme, self).save(*args, **kwargs)
                    break
                except IntegrityError:
                    if x > 50:
                        raise Exception('Cant save group: {}'.format(self.title))
            self.slug = '%s-%d' % (orig, x)

    @property
    def theme_channel(self):
        return "{}-theme".format(self.id)


class LikeGroupTheme(models.Model):
    theme = models.ForeignKey(GroupTheme, related_name='like_theme', on_delete=models.CASCADE)
    by_user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        unique_together = ('theme', 'by_user')


class HateGroupTheme(models.Model):
    theme = models.ForeignKey(GroupTheme, related_name='hate_theme', on_delete=models.CASCADE)
    by_user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('theme', 'by_user')


class LikeGroupQuerySet(models.QuerySet):
    def has_like(self, group_id, user_id):
        """
        :param user_id: ID del usuario del que se quiere comprobar
        si da me gusta al grupo
        :param group_id: ID del grupo del que se quiere saber
        si un usuario le gusta
        :return: Si un usuario es le gusta o no del grupo
        """
        return self.filter(from_like=user_id, to_like=group_id).exists()


class LikeGroupManager(models.Manager):
    def get_queryset(self):
        return LikeGroupQuerySet(self.model, using=self._db)

    def has_like(self, group_id, user_id):
        return self.filter(from_like=user_id, to_like=group_id).exists()


class LikeGroup(models.Model):
    """
    Modelo que relaciona a un usuario al dar "me gusta" a un grupo.
        <<from_like>>: Persona que da like
        <<to_like>>: Grupo que recibe el like
        <<created>>: Fecha de creación del like
    """

    class Meta:
        unique_together = ('from_like', 'to_like')

    from_like = models.ForeignKey(User, related_name='from_likegroup', on_delete=models.CASCADE)
    to_like = models.ForeignKey(UserGroups, related_name='to_likegroup', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    objects = LikeGroupManager()

    def __str__(self):
        return "Emitter: {0} Receiver: {1} Created: {2}".format(self.from_like.username, self.to_like.name,
                                                                self.created)


class RequestGroupManager(models.Manager):
    def get_follow_request(self, from_profile, to_group):
        """
        Devuelve la petición de seguimiento de un perfil
        :param profile => Perfil del que se quiere recuperar la solicitud de seguimiento:
        :return Devuelve la petición de seguimiento de un perfil:
        """
        return self.get(emitter_id=from_profile,
                        receiver_id=to_group, status=REQUEST_FOLLOWING)

    def add_follow_request(self, from_profile, to_group):
        """
        Añade una solicitud de seguimiento
        :param profile => Perfil que quiero seguir:
        :param notify => Notificacion generada:
        """
        obj, created = self.get_or_create(emitter_id=from_profile,
                                          receiver_id=to_group,
                                          status=REQUEST_FOLLOWING)
        # Si existe la peticion de amistad, actualizamos la notificacion
        obj.save()
        return obj

    def remove_received_follow_request(self, from_profile, to_group):
        """
        Elimina la petición de seguimiento hacia un perfil
        :param profile => Perfil del que se quiere eliminar una petición de seguimiento:
        """
        try:
            request = self.get(emitter_id=from_profile, receiver_id=to_group, status=REQUEST_FOLLOWING)
            request.delete()
            return True
        except ObjectDoesNotExist:
            return False


class RequestGroup(models.Model):
    """
        Modelo que gestiona las peticiones de amistad:
            <<emitter>>: Emisor de la petición
            <<receiver>>: Receptor de la petición
            <<status>>: Estado en el que se encuentra la petición
            <<created>>: Fecha en la que se creó la petición
            <<notification>>: Notificación asociada a la petición
    """
    emitter = models.ForeignKey(User, related_name='from_group_request', on_delete=models.CASCADE)
    receiver = models.ForeignKey(UserGroups, related_name='to_group_request', on_delete=models.CASCADE)
    status = models.IntegerField(choices=REQUEST_STATUSES)
    created = models.DateTimeField(auto_now_add=True)
    objects = RequestGroupManager()

    class Meta:
        unique_together = ('emitter', 'receiver', 'status')
