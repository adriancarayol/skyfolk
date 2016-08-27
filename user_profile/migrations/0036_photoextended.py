# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        ('photologue', '0010_auto_20160105_1307'),
        ('user_profile', '0035_galleryextended'),
    ]

    operations = [
        migrations.CreateModel(
            name='PhotoExtended',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('photo', models.OneToOneField(related_name='photo_extended', to='photologue.Photo')),
                ('tags', taggit.managers.TaggableManager(verbose_name='Tags', through='taggit.TaggedItem', help_text='A comma-separated list of tags.', to='taggit.Tag', blank=True)),
            ],
            options={
                'verbose_name': 'Extra fields',
            },
        ),
    ]
