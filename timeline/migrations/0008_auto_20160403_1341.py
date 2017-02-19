# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('timeline', '0007_timeline_users_add_me'),
    ]

    operations = [
        migrations.AddField(
            model_name='timeline',
            name='count_of_users',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='timeline',
            name='users_add_me',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL, related_name='users_add_me'),
        ),
    ]
