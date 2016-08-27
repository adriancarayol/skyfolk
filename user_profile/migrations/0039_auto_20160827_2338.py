# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0038_auto_20160827_2334'),
    ]

    operations = [
        migrations.AlterField(
            model_name='galleryextended',
            name='owner',
            field=models.ForeignKey(blank=True, related_name='user_gallery', default=None, null=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='photoextended',
            name='owner',
            field=models.ForeignKey(blank=True, related_name='user_photos', default=None, null=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
