# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0025_auto_20160329_1306'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='publication',
            name='is_response_from',
        ),
        migrations.RemoveField(
            model_name='publication',
            name='profile',
        ),
        migrations.AlterField(
            model_name='publication',
            name='author',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='publications'),
        ),
        migrations.AlterField(
            model_name='publication',
            name='parent',
            field=models.ForeignKey(blank=True, to='publications.Publication', null=True, related_name='reply'),
        ),
    ]
