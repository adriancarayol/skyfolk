# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0031_publication_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publication',
            name='tags',
            field=taggit.managers.TaggableManager(to='taggit.Tag', blank=True, help_text='A comma-separated list of tags.', through='taggit.TaggedItem', verbose_name='Tags'),
        ),
    ]
