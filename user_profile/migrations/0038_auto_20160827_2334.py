# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0037_auto_20160827_2327'),
    ]

    operations = [
        migrations.AlterField(
            model_name='galleryextended',
            name='owner',
            field=models.ForeignKey(default=None, related_name='user_gallery', null=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='photoextended',
            name='owner',
            field=models.ForeignKey(default=None, related_name='user_photos', null=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
