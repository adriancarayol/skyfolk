# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('publications', '0027_publication_board_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='publication',
            name='user_share_me',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL, related_name='share_me'),
        ),
    ]
