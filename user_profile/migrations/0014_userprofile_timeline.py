# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('timeline', '0001_initial'),
        ('user_profile', '0013_userprofile_backimage'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='timeline',
            field=models.ManyToManyField(to='user_profile.UserProfile', related_name='timeline_to', through='timeline.Timeline'),
        ),
    ]
