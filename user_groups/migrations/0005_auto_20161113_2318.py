# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('user_groups', '0004_auto_20161113_2318'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usergroups',
            name='users',
            field=models.ManyToManyField(related_name='users_in_group', blank=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
