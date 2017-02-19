# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('user_profile', '0031_auto_20160720_1444'),
        ('timeline', '0012_auto_20160720_2104'),
    ]

    operations = [
        migrations.AddField(
            model_name='timeline',
            name='author',
            field=models.ForeignKey(to='user_profile.UserProfile', null=True, related_name='from_timeline'),
        ),
    ]
