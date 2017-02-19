# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('publications', '0010_publication_mlikes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publication',
            name='mlikes',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
