# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('user_profile', '0040_auto_20160827_2339'),
    ]

    operations = [
        migrations.AddField(
            model_name='galleryextended',
            name='owner',
            field=models.ForeignKey(blank=True, default=None, null=True, to=settings.AUTH_USER_MODEL,
                                    related_name='user_gallery'),
        ),
        migrations.AddField(
            model_name='photoextended',
            name='owner',
            field=models.ForeignKey(blank=True, default=None, null=True, to=settings.AUTH_USER_MODEL,
                                    related_name='user_photos'),
        ),
    ]
