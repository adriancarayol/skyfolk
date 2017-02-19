# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('user_profile', '0018_userprofile_firstlogin'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='hiddenMenu',
            field=models.BooleanField(default=False),
        ),
    ]
