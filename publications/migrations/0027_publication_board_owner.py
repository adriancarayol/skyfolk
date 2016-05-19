# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('publications', '0026_auto_20160407_1552'),
    ]

    operations = [
        migrations.AddField(
            model_name='publication',
            name='board_owner',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='board_owner', default=1),
            preserve_default=False,
        ),
    ]
