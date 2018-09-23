from django.contrib.auth.models import User
from django.db import models

from publications.models import PublicationBase


class PublicationBlogManager(models.Manager):
    list_display = ['tag_list']

    def tag_list(self, obj):
        """
        Devuelve los tags de una publicación
        """
        return u", ".join(o.name for o in obj.tags.all())


class PublicationBlog(PublicationBase):
    """
    Modelo para las publicaciones de usuario (en perfiles de usuarios)
    """
    author = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', blank=True, null=True,
                               related_name='reply', on_delete=models.CASCADE)

    objects = PublicationBlogManager()
