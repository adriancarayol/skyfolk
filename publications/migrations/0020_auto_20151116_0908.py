# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0019_hashtag'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='publication',
            name='mlikes',
        ),
        migrations.AddField(
            model_name='publication',
            name='likes',
            field=models.IntegerField(default=0),
        ),
    ]
