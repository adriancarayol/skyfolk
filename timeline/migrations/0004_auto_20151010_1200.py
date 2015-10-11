# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('timeline', '0003_auto_20151010_1157'),
    ]

    operations = [
        migrations.RenameField(
            model_name='timeline',
            old_name='author',
            new_name='profile',
        ),
    ]
