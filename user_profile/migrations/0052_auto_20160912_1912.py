# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import user_profile.models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0051_auto_20160912_1912'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='backImage',
            field=models.ImageField(verbose_name='BackImage', null=True, upload_to=user_profile.models.uploadBackImagePath, blank=True),
        ),
    ]
