# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-08-15 14:05
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('publications_groups', '0004_auto_20180706_1407'),
        ('publications', '0004_auto_20180815_1352'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='publication',
            unique_together=set([('shared_publication', 'author'), ('shared_group_publication', 'author'), ('board_owner', 'id')]),
        ),
    ]
