# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0009_userprofile_backimage'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='edgeRank',
            field=models.NullBooleanField(),
        ),
    ]
