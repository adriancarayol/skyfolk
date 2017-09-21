# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-21 15:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('themes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='publicationtheme',
            name='event_type',
            field=models.IntegerField(choices=[(1, 'publication'), (2, 'new_relation'), (3, 'link'), (4, 'relevant'), (5, 'imagen'), (6, 'shared'), (7, 'shared_photo_pub'), (8, 'shared_group_pub')], default=1),
        ),
    ]
