# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import taggit.managers
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('photologue', '0010_auto_20160105_1307'),
        ('taggit', '0002_auto_20150616_2121'),
        ('user_profile', '0047_auto_20160827_2356'),
    ]

    operations = [
        migrations.CreateModel(
            name='GalleryExtended',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('gallery', models.OneToOneField(to='photologue.Gallery', related_name='gallery_extended')),
                ('owner',
                 models.ForeignKey(to=settings.AUTH_USER_MODEL, blank=True, related_name='user_gallery', null=True)),
                ('tags',
                 taggit.managers.TaggableManager(verbose_name='Tags', help_text='A comma-separated list of tags.',
                                                 to='taggit.Tag', blank=True, through='taggit.TaggedItem')),
            ],
            options={
                'verbose_name': 'Extra fields',
            },
        ),
        migrations.CreateModel(
            name='PhotoExtended',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('owner',
                 models.ForeignKey(to=settings.AUTH_USER_MODEL, blank=True, related_name='user_photos', null=True)),
                ('photo', models.OneToOneField(to='photologue.Photo', related_name='photo_extended')),
                ('tags',
                 taggit.managers.TaggableManager(verbose_name='Tags', help_text='A comma-separated list of tags.',
                                                 to='taggit.Tag', blank=True, through='taggit.TaggedItem')),
            ],
            options={
                'verbose_name': 'Extra fields',
            },
        ),
    ]
