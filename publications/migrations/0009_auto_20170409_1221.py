# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-09 10:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0008_auto_20170409_1217'),
    ]

    operations = [
        migrations.AlterField(
            model_name='extracontent',
            name='image',
            field=models.URLField(blank=True, null=True),
        ),
    ]
