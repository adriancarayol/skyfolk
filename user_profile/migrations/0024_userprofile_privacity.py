# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0023_auto_20160417_1124'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='privacity',
            field=models.CharField(default='A', choices=[('OF', 'OnlyFo'), ('OFAF', 'OnlyFAF'), ('A', 'All'), ('N', 'Nothing')], max_length=4),
        ),
    ]
