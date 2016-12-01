# encoding:utf-8
from django.db import models
from django.contrib.auth.models import User
from taggit.managers import TaggableManager
from django.utils.text import slugify

def upload_small_group_image(instance, filename):
    return '%s/small_group_image/%s' % (instance.name, filename)

def upload_large_group_image(instance, filename):
    return '%s/large_group_image/%s' % (instance.name, filename)


class UserGroupsQuerySet(models.QuerySet):
    """
    QuerySet para UserGroups
    """
    pass

class UserGroupsManager(models.Manager):
    """
    Manager para UserGroups
    """
    pass

class UserGroups(models.Model):
    """
        Modelo para la creacion de grupos de usuarios.
    """
    name = models.CharField(max_length=128, unique=True)
    slug = models.SlugField(max_length=256, unique=True, null=True)
    description = models.TextField(max_length=1024, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=32, blank=True, null=True)
    owner = models.ForeignKey(User, related_name='group_owner')
    users = models.ManyToManyField(User, related_name='users_in_group', blank=True)
    small_image = models.ImageField(upload_to=upload_small_group_image, verbose_name='small_image',
                                    blank=True, null=True)
    large_image = models.ImageField(upload_to=upload_large_group_image, verbose_name='large_image',
                                    blank=True, null=True)
    privacity = models.BooleanField(default=True, help_text='Desactiva esta casilla si quieres que el grupo sea privado.')
    tags = TaggableManager()

    objects = UserGroupsManager()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.slug = slugify(self.name)
        super(UserGroups, self).save(force_insert=force_insert, force_update=force_update,
                                     using=using, update_fields=update_fields)


#TODO
class RolUserGroup(models.Model):
    """
    Establece un rol para un usuario especifico
    dentro de un grupo.
    """
    pass