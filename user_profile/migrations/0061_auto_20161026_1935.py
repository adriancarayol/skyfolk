# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('user_profile', '0060_auto_20161026_1032'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='is_first_time_login',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='is_first_login',
            field=models.BooleanField(default=False),
        ),
    ]
