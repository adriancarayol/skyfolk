# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('timeline', '0006_timeline_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='timeline',
            name='users_add_me',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, related_name='users_add_me'),
        ),
    ]
