# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0025_remove_userprofile_publications'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='image',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='avatar_path',
            field=models.TextField(null=True, blank=True, validators=[django.core.validators.URLValidator()]),
        ),
    ]
