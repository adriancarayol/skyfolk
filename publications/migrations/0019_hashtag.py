# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0018_auto_20151114_1637'),
    ]

    operations = [
        migrations.CreateModel(
            name='Hashtag',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(unique=True, max_length=64)),
                ('publicacion', models.ManyToManyField(to='publications.Publication')),
            ],
            options={
                'ordering': ('name',),
                'verbose_name_plural': 'hashtags',
                'verbose_name': 'hashtag',
            },
        ),
    ]
