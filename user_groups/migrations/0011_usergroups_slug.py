# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_groups', '0010_auto_20161114_1146'),
    ]

    operations = [
        migrations.AddField(
            model_name='usergroups',
            name='slug',
            field=models.SlugField(max_length=256, null=True, unique=True),
        ),
    ]
