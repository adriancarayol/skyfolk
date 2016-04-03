# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0022_userprofile_hiddenmenu'),
        ('timeline', '0010_auto_20160403_1544'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='timeline',
            name='profile',
        ),
        migrations.AddField(
            model_name='timeline',
            name='profile',
            field=models.ForeignKey(to='user_profile.UserProfile', default='', related_name='to_timeline'),
            preserve_default=False,
        ),
    ]
