# encoding:utf-8
from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify
from taggit.managers import TaggableManager
from django.contrib.auth.models import Group

def upload_small_group_image(instance, filename):
    return '%s/small_group_image/%s' % (instance.name, filename)


def upload_large_group_image(instance, filename):
    return '%s/large_group_image/%s' % (instance.name, filename)


class RolUserGroup(models.Model):
    """
    Establece un rol para un usuario especifico
    dentro de un grupo.
    """
    ROL_CHOICES = (
        ('A', 'Admin'),
        ('M', 'Mod'),
        ('N', 'Normal'),
    )
    user = models.ForeignKey(User, related_name='rol_user', blank=True, null=True)
    rol = models.CharField(max_length=1, choices=ROL_CHOICES, default='A')

    def get_rol_verbose(self):
        return dict(RolUserGroup.ROL_CHOICES)[self.rol]


class UserGroupsQuerySet(models.QuerySet):
    """
    QuerySet para UserGroups
    """

    def get_normal(self):
        """
        :return: Los usuarios con el rol normal
        """
        return self.filter(users__rol='N')

    def get_admin(self):
        """
        :return: Los usuarios con el rol administrador
        """
        return self.filter(users__rol='A')

    def get_mod(self):
        """
        Devuelve los usuarios con el rot mod
        :return: Los usuarios con el rol mod
        """
        return self.filter(users__rol='M')

    def is_follow(self, group_id, user_id):
        """
        :param user_id: ID del usuario del que se quiere comprobar
        si es seguidor del grupo
        :param group_id: ID del grupo del que se quiere saber
        si un usuario lo sigue
        :return: Si un usuario es seguidor o no del grupo
        """
        return self.filter(id=group_id, users__user=user_id).exists()


class UserGroupsManager(models.Manager):
    """
    Manager para UserGroups
    """

    def get_queryset(self):
        return UserGroupsQuerySet(self.model, using=self._db)

    def get_normal(self):
        return self.get_queryset().get_normal()

    def get_admin(self):
        return self.get_queryset().get_admin()

    def get_mod(self):
        return self.get_queryset().get_mod()

    def is_follow(self, group_id, user_id):
        return self.get_queryset().is_follow(group_id=group_id, user_id=user_id)


class UserGroups(Group):
    """
        Modelo para la creacion de grupos de usuarios.
    """
    # name = models.CharField(max_length=128, unique=True)
    slug = models.SlugField(max_length=256, unique=True, null=True)
    description = models.TextField(max_length=1024, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=32, blank=True, null=True)
    owner = models.ForeignKey(User, related_name='group_owner')
    users = models.ManyToManyField(RolUserGroup,
                                   related_name='users_in_group', blank=True)
    small_image = models.ImageField(upload_to=upload_small_group_image,
                                    verbose_name='small_image',
                                    blank=True, null=True)
    large_image = models.ImageField(upload_to=upload_large_group_image,
                                    verbose_name='large_image',
                                    blank=True, null=True)
    privacity = models.BooleanField(default=True,
                                    help_text='Desactiva esta casilla '
                                              'si quieres que el grupo sea privado.')
    tags = TaggableManager()

    objects = UserGroupsManager()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.slug = slugify(self.name)
        super(UserGroups, self).save()


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
        get_latest_by = 'created'
        unique_together = ('from_like', 'to_like')

    from_like = models.ForeignKey(User, related_name='from_likegroup')
    to_like = models.ForeignKey(UserGroups, related_name='to_likegroup')
    created = models.DateTimeField(auto_now_add=True)

    objects = LikeGroupManager()

    def __str__(self):
        return "Emitter: {0} Receiver: {1} Created: {2}".format(self.from_like.username, self.to_like.name,
                                                                self.created)
