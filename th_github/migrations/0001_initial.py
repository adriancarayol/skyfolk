# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-22 21:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('skyfolk', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Github',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('status', models.BooleanField(default=False)),
                ('description', models.CharField(max_length=255)),
                ('repo', models.CharField(max_length=80)),
                ('project', models.CharField(max_length=80)),
                ('trigger', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='skyfolk.TriggerService')),
            ],
            options={
                'db_table': 'skyfolk_github',
            },
        ),
    ]
