# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('user_profile', '0022_userprofile_hiddenmenu'),
        ('timeline', '0009_timeline_publication'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='timeline',
            name='profile',
        ),
        migrations.AddField(
            model_name='timeline',
            name='profile',
            field=models.ManyToManyField(related_name='to_timeline', blank=True, to='user_profile.UserProfile'),
        ),
    ]
