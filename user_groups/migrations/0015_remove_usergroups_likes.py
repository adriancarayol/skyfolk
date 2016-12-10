# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_groups', '0014_auto_20161210_1633'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usergroups',
            name='likes',
        ),
    ]
