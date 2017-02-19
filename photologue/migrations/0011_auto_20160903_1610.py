# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import taggit.managers
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('photologue', '0010_auto_20160105_1307'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='owner',
            field=models.ForeignKey(related_name='user_photos', to=settings.AUTH_USER_MODEL, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='photo',
            name='tags',
            field=taggit.managers.TaggableManager(to='taggit.Tag', verbose_name='Tags', blank=True,
                                                  help_text='A comma-separated list of tags.',
                                                  through='taggit.TaggedItem'),
        ),
        migrations.AlterField(
            model_name='photo',
            name='slug',
            field=models.SlugField(max_length=250, verbose_name='slug',
                                   help_text='A "slug" is a unique URL-friendly title for an object.'),
        ),
        migrations.AlterField(
            model_name='photo',
            name='title',
            field=models.CharField(max_length=250, verbose_name='title'),
        ),
    ]
