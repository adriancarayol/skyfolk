# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('user_profile', '0055_auto_20161021_1909'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='favouriteusers',
            name='emitter',
        ),
        migrations.RemoveField(
            model_name='favouriteusers',
            name='receiver',
        ),
        migrations.DeleteModel(
            name='FavouriteUsers',
        ),
    ]
