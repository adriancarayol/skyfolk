# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('user_profile', '0020_auto_20160113_1335'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='hiddenMenu',
        ),
    ]
