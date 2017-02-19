# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('user_profile', '0042_auto_20160827_2346'),
    ]

    operations = [
        migrations.AlterField(
            model_name='galleryextended',
            name='owner',
            field=models.ForeignKey(null=True, blank=True, to='user_profile.UserProfile', related_name='user_gallery'),
        ),
        migrations.AlterField(
            model_name='photoextended',
            name='owner',
            field=models.ForeignKey(null=True, blank=True, to='user_profile.UserProfile', related_name='user_photos'),
        ),
    ]
