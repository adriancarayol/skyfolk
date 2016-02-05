# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import achievements.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Achievements',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('description', models.CharField(max_length=145)),
                ('points', models.IntegerField(default=0, choices=[('I', 1), ('V', 5), ('X', 10), ('L', 50), ('C', 100), ('D', 500), ('M', 1000)])),
                ('image', models.ImageField(upload_to=achievements.models.uploadAchievementsPath, null=True, blank=True, verbose_name='image')),
            ],
        ),
    ]
