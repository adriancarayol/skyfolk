# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('publications', '0014_auto_20151023_1148'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publication',
            name='user_give_me_like',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
