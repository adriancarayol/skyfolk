# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('publications', '0006_auto_20150920_1359'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='publication',
            name='isPrivate',
        ),
    ]
