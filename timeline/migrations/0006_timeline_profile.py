# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('user_profile', '0022_userprofile_hiddenmenu'),
        ('timeline', '0005_auto_20151011_1333'),
    ]

    operations = [
        migrations.AddField(
            model_name='timeline',
            name='profile',
            field=models.ForeignKey(to='user_profile.UserProfile', related_name='to_timeline', default=''),
            preserve_default=False,
        ),
    ]
