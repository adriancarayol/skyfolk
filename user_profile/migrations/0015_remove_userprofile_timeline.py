# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0014_userprofile_timeline'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='timeline',
        ),
    ]
