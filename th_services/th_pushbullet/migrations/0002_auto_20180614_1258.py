# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-14 10:58
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('th_pushbullet', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pushbullet',
            name='trigger',
        ),
        migrations.DeleteModel(
            name='Pushbullet',
        ),
    ]
