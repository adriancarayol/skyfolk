# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('achievements', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='achievements',
            name='unlock',
            field=models.BooleanField(default=False),
        ),
    ]
