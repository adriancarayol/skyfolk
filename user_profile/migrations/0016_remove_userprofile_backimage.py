# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-12 00:18
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0015_auto_20170610_2105'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='backImage',
        ),
    ]
