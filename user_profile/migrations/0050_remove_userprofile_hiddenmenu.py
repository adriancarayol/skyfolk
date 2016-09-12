# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0049_auto_20160830_1808'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='hiddenMenu',
        ),
    ]
