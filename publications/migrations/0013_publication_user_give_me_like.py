# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0016_userprofile_timeline'),
        ('publications', '0012_auto_20151023_1131'),
    ]

    operations = [
        migrations.AddField(
            model_name='publication',
            name='user_give_me_like',
            field=models.ManyToManyField(to='user_profile.UserProfile'),
        ),
    ]
