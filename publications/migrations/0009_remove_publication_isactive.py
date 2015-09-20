# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0008_publication_isactive'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='publication',
            name='isActive',
        ),
    ]
