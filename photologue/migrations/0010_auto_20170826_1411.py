# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-26 12:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photologue', '0009_auto_20170826_1410'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photogroup',
            name='url_image',
            field=models.URLField(blank=True, default='', max_length=255),
        ),
    ]
