# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0019_userprofile_hiddenmenu'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='hiddenMenu',
            field=models.BooleanField(default=True),
        ),
    ]
