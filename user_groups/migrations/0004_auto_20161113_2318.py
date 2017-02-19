# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import taggit.managers
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        ('user_groups', '0003_auto_20161113_2218'),
    ]

    operations = [
        migrations.AddField(
            model_name='usergroups',
            name='tags',
            field=taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem',
                                                  help_text='A comma-separated list of tags.', verbose_name='Tags'),
        ),
        migrations.AlterField(
            model_name='usergroups',
            name='users',
            field=models.ManyToManyField(null=True, to=settings.AUTH_USER_MODEL, related_name='users_in_group',
                                         blank=True),
        ),
    ]
