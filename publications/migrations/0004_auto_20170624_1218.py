# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-24 10:18
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0003_auto_20170621_1336'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='sharedpublication',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='sharedpublication',
            name='by_user',
        ),
        migrations.RemoveField(
            model_name='sharedpublication',
            name='publication',
        ),
        migrations.AlterField(
            model_name='publication',
            name='shared_publication',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='publications.Publication'),
        ),
        migrations.DeleteModel(
            name='SharedPublication',
        ),
    ]
