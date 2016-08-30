# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0048_galleryextended_photoextended'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='galleryextended',
            name='gallery',
        ),
        migrations.RemoveField(
            model_name='galleryextended',
            name='owner',
        ),
        migrations.RemoveField(
            model_name='galleryextended',
            name='tags',
        ),
        migrations.RemoveField(
            model_name='photoextended',
            name='owner',
        ),
        migrations.RemoveField(
            model_name='photoextended',
            name='photo',
        ),
        migrations.RemoveField(
            model_name='photoextended',
            name='tags',
        ),
        migrations.DeleteModel(
            name='GalleryExtended',
        ),
        migrations.DeleteModel(
            name='PhotoExtended',
        ),
    ]
