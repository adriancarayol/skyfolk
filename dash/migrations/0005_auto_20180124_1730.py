# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-24 16:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dash', '0004_auto_20171113_2205'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dashboardsettings',
            name='allow_different_layouts',
            field=models.BooleanField(default=True, help_text='Allows you to use different layouts for each workspace.', verbose_name='Allow different layouts per workspace?'),
        ),
    ]
