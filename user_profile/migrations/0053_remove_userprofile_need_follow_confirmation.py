# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0052_auto_20160912_1912'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='need_follow_confirmation',
        ),
    ]
