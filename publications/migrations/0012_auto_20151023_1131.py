# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('publications', '0011_auto_20151015_0019'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publication',
            name='mlikes',
            field=models.IntegerField(blank=True, default=0),
        ),
    ]
