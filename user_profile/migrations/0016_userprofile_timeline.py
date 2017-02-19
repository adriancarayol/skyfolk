# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('timeline', '0002_timeline_profile'),
        ('user_profile', '0015_remove_userprofile_timeline'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='timeline',
            field=models.ManyToManyField(related_name='timeline_to', through='timeline.Timeline',
                                         to='user_profile.UserProfile'),
        ),
    ]
