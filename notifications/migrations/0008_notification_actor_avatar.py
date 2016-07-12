# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0007_auto_20160712_1209'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='actor_avatar',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
