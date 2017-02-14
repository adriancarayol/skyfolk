# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('publications', '0020_auto_20160302_2127'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publication',
            name='user_give_me_like',
            field=models.ManyToManyField(blank=True, to='user_profile.UserProfile'),
        ),
    ]
