# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('user_profile', '0015_remove_userprofile_timeline'),
        ('timeline', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='timeline',
            name='profile',
            field=models.ForeignKey(related_name='to_timeline', to='user_profile.UserProfile', null=True),
        ),
    ]
