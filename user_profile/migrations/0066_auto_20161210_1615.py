# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('user_profile', '0065_auto_20161113_1641'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='likeprofile',
            options={'get_latest_by': 'created'},
        ),
    ]
