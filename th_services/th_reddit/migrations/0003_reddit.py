# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-14 15:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('dash_services', '0001_initial'),
        ('th_reddit', '0002_auto_20180614_1258'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reddit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('status', models.BooleanField(default=False)),
                ('description', models.CharField(max_length=255)),
                ('subreddit', models.CharField(max_length=80)),
                ('share_link', models.BooleanField(default=False)),
                ('trigger', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dash_services.TriggerService')),
            ],
            options={
                'db_table': 'skyfolk_reddit',
            },
        ),
    ]
