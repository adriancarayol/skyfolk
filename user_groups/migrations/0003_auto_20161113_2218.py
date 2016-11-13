# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('user_groups', '0002_auto_20161113_2218'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usergroups',
            name='owner',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='group_owner'),
        ),
    ]
