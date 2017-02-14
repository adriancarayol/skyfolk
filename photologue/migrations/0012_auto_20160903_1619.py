# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('photologue', '0011_auto_20160903_1610'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='slug',
            field=models.SlugField(verbose_name='slug', max_length=250, unique=True,
                                   help_text='A "slug" is a unique URL-friendly title for an object.'),
        ),
    ]
