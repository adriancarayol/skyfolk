# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0027_remove_userprofile_avatar_path'),
    ]

    operations = [
        migrations.AlterField(
            model_name='relationship',
            name='status',
            field=models.IntegerField(choices=[(1, 'Following'), (2, 'Follower'), (3, 'Blocked')]),
        ),
        migrations.AlterField(
            model_name='request',
            name='status',
            field=models.IntegerField(choices=[(1, 'Following'), (2, 'Follower'), (3, 'Blocked')]),
        ),
    ]
