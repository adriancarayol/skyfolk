# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-01 09:40
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('photologue_groups', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='photogroup',
            name='is_public',
        ),
        migrations.RemoveField(
            model_name='videogroup',
            name='is_public',
        ),
    ]
