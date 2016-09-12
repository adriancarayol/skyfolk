# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import user_profile.models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0050_remove_userprofile_hiddenmenu'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='backImage',
            field=models.ImageField(upload_to=user_profile.models.uploadBackImagePath, default='/static/img/nuevo_back.png', blank=True, null=True, verbose_name='BackImage'),
        ),
    ]
