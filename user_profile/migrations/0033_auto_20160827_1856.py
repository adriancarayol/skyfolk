# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photologue', '0010_auto_20160105_1307'),
        ('user_profile', '0032_auto_20160820_1235'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='gallery',
            field=models.ManyToManyField(to='photologue.Gallery', related_name='user_gallery'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='photos',
            field=models.ManyToManyField(to='photologue.Photo', related_name='user_photos'),
        ),
    ]
