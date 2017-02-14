# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('publications', '0015_auto_20151026_1910'),
    ]

    operations = [
        migrations.RenameField(
            model_name='publication',
            old_name='writer',
            new_name='author',
        ),
    ]
