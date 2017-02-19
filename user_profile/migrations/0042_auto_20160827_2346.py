# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('user_profile', '0041_auto_20160827_2344'),
    ]

    operations = [
        migrations.AlterField(
            model_name='galleryextended',
            name='owner',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, blank=True, related_name='user_gallery'),
        ),
        migrations.AlterField(
            model_name='photoextended',
            name='owner',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, blank=True, related_name='user_photos'),
        ),
    ]
