# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0003_userprofile_backgroundimage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='backgroundimage',
        ),
    ]
