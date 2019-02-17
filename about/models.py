from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import truncatechars_html
from django.utils.html import format_html
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
    title = models.CharField(max_length=128, default="")
    author = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', blank=True, null=True,
                               related_name='reply', on_delete=models.CASCADE)

    objects = PublicationBlogManager()

    @property
    def short_content(self):
        return truncatechars_html(format_html(self.content), 100)

    
    def parse_content(self):
        pass
