# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('timeline', '0015_auto_20160720_2122'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='timeline',
            name='users_add_me',
        ),
    ]
