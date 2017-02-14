# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('user_profile', '0024_userprofile_privacity'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='publications',
        ),
    ]
