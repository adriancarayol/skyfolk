# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import taggit.managers
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        ('user_profile', '0061_auto_20161026_1935'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='tags',
            field=taggit.managers.TaggableManager(blank=True, help_text='A comma-separated list of tags.',
                                                  through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='is_first_login',
            field=models.BooleanField(default=True),
        ),
    ]
