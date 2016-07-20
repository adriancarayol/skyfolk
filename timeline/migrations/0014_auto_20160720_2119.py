# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timeline', '0013_timeline_author'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timeline',
            name='publication',
            field=models.ForeignKey(to='publications.Publication', related_name='pubs_timeline', null=True),
        ),
    ]
