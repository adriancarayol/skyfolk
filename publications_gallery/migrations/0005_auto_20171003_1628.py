# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-03 14:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('publications_gallery', '0004_auto_20170927_1717'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publicationphoto',
            name='event_type',
            field=models.IntegerField(choices=[(1, 'publication'), (2, 'new_relation'), (3, 'link'), (4, 'relevant'), (5, 'imagen'), (6, 'shared')], default=1),
        ),
        migrations.AlterField(
            model_name='publicationvideo',
            name='event_type',
            field=models.IntegerField(choices=[(1, 'publication'), (2, 'new_relation'), (3, 'link'), (4, 'relevant'), (5, 'imagen'), (6, 'shared')], default=1),
        ),
    ]
