# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('publications', '0007_remove_publication_isprivate'),
    ]

    operations = [
        migrations.AddField(
            model_name='publication',
            name='isActive',
            field=models.NullBooleanField(),
        ),
    ]
