# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-07-07 15:20
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dash_contrib_plugins_twitch', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='pollresponse',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='pollresponse',
            name='poll',
        ),
        migrations.RemoveField(
            model_name='pollresponse',
            name='user',
        ),
        migrations.DeleteModel(
            name='PollResponse',
        ),
    ]
