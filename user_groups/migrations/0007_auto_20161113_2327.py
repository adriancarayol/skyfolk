# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_groups', '0006_auto_20161113_2325'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usergroups',
            name='created',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
