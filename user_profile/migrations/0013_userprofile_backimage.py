# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

import user_profile.models


class Migration(migrations.Migration):
    dependencies = [
        ('user_profile', '0012_remove_userprofile_backimage'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='backImage',
            field=models.ImageField(null=True, upload_to=user_profile.models.uploadBackImagePath,
                                    verbose_name='BackImage', blank=True),
        ),
    ]
