# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('user_groups', '0007_auto_20161113_2327'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usergroups',
            name='description',
            field=models.TextField(null=True, blank=True, max_length=1024),
        ),
    ]
