# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import user_profile.models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0002_remove_userprofile_favorite_animal'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='backgroundimage',
            field=models.ImageField(blank=True, null=True, verbose_name='backImage', upload_to=user_profile.models.uploadAvatarPath),
        ),
    ]
