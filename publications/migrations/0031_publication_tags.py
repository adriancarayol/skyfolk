# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import taggit.managers
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        ('publications', '0030_auto_20160726_2031'),
    ]

    operations = [
        migrations.AddField(
            model_name='publication',
            name='tags',
            field=taggit.managers.TaggableManager(through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags',
                                                  help_text='A comma-separated list of tags.'),
        ),
    ]
