# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0033_auto_20160827_1856'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='gallery',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='photos',
        ),
    ]
