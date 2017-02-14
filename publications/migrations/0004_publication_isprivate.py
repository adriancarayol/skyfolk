# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('publications', '0003_auto_20150917_0421'),
    ]

    operations = [
        migrations.AddField(
            model_name='publication',
            name='isPrivate',
            field=models.BooleanField(default=False),
        ),
    ]
