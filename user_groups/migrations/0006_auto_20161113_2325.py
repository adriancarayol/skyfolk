# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('user_groups', '0005_auto_20161113_2318'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usergroups',
            name='description',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='usergroups',
            name='type',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
    ]
