# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0034_auto_20160827_1857'),
        ('photologue', '0010_auto_20160105_1307'),
    ]

    operations = [
        migrations.AddField(
            model_name='gallery',
            name='owner',
            field=models.ForeignKey(to='user_profile.UserProfile', related_name='gallery_owner', null=True),
        ),
        migrations.AddField(
            model_name='photo',
            name='owner',
            field=models.ForeignKey(to='user_profile.UserProfile', related_name='photo_owner', null=True),
        ),
    ]
