from publications.models import PublicationBase
from django.contrib.auth.models import User
from user_groups.models import UserGroups
from django.db import models


class PublicationGroup(PublicationBase):
    author = models.ForeignKey(User)
    board_group = models.ForeignKey(UserGroups, db_index=True)
    parent = models.ForeignKey('self', blank=True, null=True,
                               related_name='reply_group')

    class Meta:
        unique_together = ('board_group', 'id')

    class MPTTMeta:
        order_insertion_by = ['-created']

    def  __str__(self):
        return self.content

