# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import taggit.managers
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('photologue', '0010_auto_20160105_1307'),
        ('taggit', '0002_auto_20150616_2121'),
        ('user_profile', '0034_auto_20160827_1857'),
    ]

    operations = [
        migrations.CreateModel(
            name='GalleryExtended',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('gallery', models.OneToOneField(related_name='gallery_extended', to='photologue.Gallery')),
                ('tags',
                 taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', verbose_name='Tags',
                                                 help_text='A comma-separated list of tags.', blank=True)),
            ],
            options={
                'verbose_name': 'Extra fields',
            },
        ),
    ]
