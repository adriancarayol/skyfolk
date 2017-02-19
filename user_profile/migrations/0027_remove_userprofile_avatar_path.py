# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('user_profile', '0026_auto_20160708_1110'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='avatar_path',
        ),
    ]
