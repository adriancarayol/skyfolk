# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('publications', '0021_auto_20160303_2347'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publication',
            name='user_give_me_like',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, blank=True),
        ),
    ]
