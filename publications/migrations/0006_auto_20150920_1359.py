# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0005_auto_20150920_1355'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publication',
            name='isPrivate',
            field=models.BooleanField(default=True),
        ),
    ]
