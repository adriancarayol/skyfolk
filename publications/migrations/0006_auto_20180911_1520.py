# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-09-11 13:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0005_auto_20180815_1605'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publication',
            name='content',
            field=models.TextField(max_length=10000),
        ),
    ]
