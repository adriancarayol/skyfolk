# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('publications', '0004_publication_isprivate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publication',
            name='isPrivate',
            field=models.BooleanField(),
        ),
    ]
