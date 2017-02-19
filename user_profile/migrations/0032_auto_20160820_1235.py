# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('user_profile', '0031_auto_20160720_1444'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='firstLogin',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='need_follow_confirmation',
            field=models.BooleanField(default=True),
        ),
    ]
