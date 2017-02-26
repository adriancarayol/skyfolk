# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-24 16:05
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dash', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dashboardplugin',
            name='groups',
            field=models.ManyToManyField(blank=True, to='auth.Group', verbose_name='Group'),
        ),
        migrations.AlterField(
            model_name='dashboardplugin',
            name='users',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL, verbose_name='User'),
        ),
    ]
