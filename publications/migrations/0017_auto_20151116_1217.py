# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0016_auto_20151116_1024'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publication',
            name='likes',
            field=models.IntegerField(null=True, default=0, blank=True),
        ),
    ]
