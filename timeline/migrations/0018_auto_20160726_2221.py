# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('timeline', '0017_auto_20160724_2135'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timeline',
            name='insertion_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
