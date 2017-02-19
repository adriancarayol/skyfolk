# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('user_profile', '0056_auto_20161025_2023'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='lastuservisit',
            unique_together=set([('emitter', 'receiver')]),
        ),
    ]
