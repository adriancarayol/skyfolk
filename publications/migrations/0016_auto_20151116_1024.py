# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0015_auto_20151026_1910'),
    ]

    operations = [
        migrations.CreateModel(
            name='Hashtag',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(unique=True, max_length=64)),
            ],
            options={
                'verbose_name_plural': 'hashtags',
                'ordering': ('name',),
                'verbose_name': 'hashtag',
            },
        ),
        migrations.RemoveField(
            model_name='publication',
            name='mlikes',
        ),
        migrations.AddField(
            model_name='publication',
            name='likes',
            field=models.IntegerField(default=0, max_length=10, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='hashtag',
            name='publicacion',
            field=models.ManyToManyField(to='publications.Publication'),
        ),
    ]
