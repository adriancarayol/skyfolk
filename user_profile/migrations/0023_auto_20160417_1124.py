# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('user_profile', '0022_userprofile_hiddenmenu'),
    ]

    operations = [
        migrations.AlterField(
            model_name='relationship',
            name='status',
            field=models.IntegerField(choices=[(1, 'Following'), (2, 'Blocked'), (3, 'Friend'), (4, 'Follower')]),
        ),
        migrations.AlterField(
            model_name='request',
            name='status',
            field=models.IntegerField(choices=[(1, 'Friend'), (2, 'Following'), (3, 'Follower'), (1, 'Friend')]),
        ),
    ]
