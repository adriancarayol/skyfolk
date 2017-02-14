# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.core.files.storage
from django.db import migrations, models

import avatar.models


class Migration(migrations.Migration):
    dependencies = [
        ('avatar', '0002_auto_20160712_1303'),
    ]

    operations = [
        migrations.AlterField(
            model_name='avatar',
            name='avatar',
            field=models.ImageField(upload_to=avatar.models.avatar_path_handler, blank=True,
                                    storage=django.core.files.storage.FileSystemStorage(), max_length=1024),
        ),
    ]
