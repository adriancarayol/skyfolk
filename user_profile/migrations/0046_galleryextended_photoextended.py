# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import taggit.managers
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        ('photologue', '0010_auto_20160105_1307'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('user_profile', '0045_auto_20160827_2354'),
    ]

    operations = [
        migrations.CreateModel(
            name='GalleryExtended',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('gallery', models.OneToOneField(to='photologue.Gallery', related_name='gallery_extended')),
                ('owner',
                 models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, related_name='user_gallery', null=True)),
                ('tags', taggit.managers.TaggableManager(to='taggit.Tag', blank=True,
                                                         help_text='A comma-separated list of tags.',
                                                         through='taggit.TaggedItem', verbose_name='Tags')),
            ],
            options={
                'verbose_name': 'Extra fields',
            },
        ),
        migrations.CreateModel(
            name='PhotoExtended',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('owner',
                 models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, related_name='user_photos', null=True)),
                ('photo', models.OneToOneField(to='photologue.Photo', related_name='photo_extended')),
                ('tags', taggit.managers.TaggableManager(to='taggit.Tag', blank=True,
                                                         help_text='A comma-separated list of tags.',
                                                         through='taggit.TaggedItem', verbose_name='Tags')),
            ],
            options={
                'verbose_name': 'Extra fields',
            },
        ),
    ]
