# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0015_auto_20151026_1910'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publication',
            name='mlikes',
            field=models.CharField(default=0, blank=True, max_length=3),
        ),
    ]
