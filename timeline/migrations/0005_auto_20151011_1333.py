# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('timeline', '0004_auto_20151010_1200'),
    ]

    operations = [
        migrations.RenameField(
            model_name='timeline',
            old_name='profile',
            new_name='author',
        ),
    ]
