# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

import user_profile.models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0008_auto_20150920_2224'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='backImage',
            field=models.ImageField(upload_to=user_profile.models.uploadBackImagePath, verbose_name='BackImage', null=True, blank=True),
        ),
    ]
