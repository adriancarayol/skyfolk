import re
from django.contrib.auth.models import User
from django.db import models
from embed_video.fields import EmbedVideoField

from publications.models import PublicationBase
from user_groups.models import UserGroups


class ExtraGroupContent(models.Model):
    """
    Modelo para contenido extra/adicional de una publicacion,
    por ejemplo, informacion resumida de una URL
    """
    title = models.CharField(max_length=64, default="")
    description = models.CharField(max_length=256, default="")
    image = models.URLField(null=True, blank=True)
    url = models.URLField()
    video = EmbedVideoField(null=True, blank=True)
    publication = models.OneToOneField('PublicationGroup', related_name='group_extra_content')


class PublicationGroup(PublicationBase):
    author = models.ForeignKey(User)
    board_group = models.ForeignKey(UserGroups, db_index=True)
    parent = models.ForeignKey('self', blank=True, null=True,
                               related_name='reply_group')
    user_give_me_like = models.ManyToManyField(User, blank=True,
                                               related_name='likes_group_publication')
    user_give_me_hate = models.ManyToManyField(User, blank=True,
                                               related_name='hates_group_publication')

    class Meta:
        unique_together = ('board_group', 'id')

    class MPTTMeta:
        order_insertion_by = ['-created']

    def __str__(self):
        return self.content

    def has_extra_content(self):
        return hasattr(self, 'group_extra_content')

    def parse_extra_content(self):
        # Buscamos en el contenido del mensaje una URL y mostramos un breve resumen de ella
        link_url = re.findall(
            r'(?:(?:https?|ftp)://)(?:\S+(?::\S*)?@)?(?:(?!(?:10|127)(?:\.\d{1,3}){3})(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)(?:\.(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,})))(?::\d{2,5})?(?:/\S*)?',
            self.content)

        if link_url and len(link_url) > 0:
            self.event_type = 3
            """
            for u in list(set(link_url)):  # Convertimos URL a hipervinculo
                self.content = self.content.replace(u, '<a href="%s">%s</a>' % (u, u))
            """


