# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import avatar.models
import django.core.files.storage


class Migration(migrations.Migration):

    dependencies = [
        ('avatar', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='avatar',
            name='avatar',
            field=models.ImageField(default='/media/img/default.png', max_length=1024, storage=django.core.files.storage.FileSystemStorage(), blank=True, upload_to=avatar.models.avatar_path_handler),
        ),
    ]
