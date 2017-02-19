# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('user_groups', '0015_remove_usergroups_likes'),
        ('publications', '0032_auto_20160926_2300'),
    ]

    operations = [
        migrations.CreateModel(
            name='PublicationGroup',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('board_group', models.ForeignKey(related_name='board_group', to='user_groups.UserGroups')),
                ('parent', models.ForeignKey(related_name='reply_group', blank=True, null=True,
                                             to='publications.PublicationGroup')),
                ('user_give_me_hate',
                 models.ManyToManyField(related_name='hates_group_me', blank=True, to=settings.AUTH_USER_MODEL)),
                ('user_give_me_like',
                 models.ManyToManyField(related_name='likes_group_me', blank=True, to=settings.AUTH_USER_MODEL)),
                ('user_share_me',
                 models.ManyToManyField(related_name='share_group_me', blank=True, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
