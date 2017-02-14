# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('user_groups', '0013_auto_20161210_1615'),
    ]

    operations = [
        migrations.AlterField(
            model_name='likegroup',
            name='from_like',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='from_likegroup'),
        ),
    ]
