# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('publications', '0025_auto_20160329_1306'),
        ('timeline', '0008_auto_20160403_1341'),
    ]

    operations = [
        migrations.AddField(
            model_name='timeline',
            name='publication',
            field=models.ForeignKey(to='publications.Publication', blank=True, null=True,
                                    related_name='publication_to_timeline'),
        ),
    ]
