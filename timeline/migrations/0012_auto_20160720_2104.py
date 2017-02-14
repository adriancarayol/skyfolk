# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('timeline', '0011_auto_20160403_1545'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='timeline',
            name='author',
        ),
        migrations.RemoveField(
            model_name='timeline',
            name='content',
        ),
        migrations.RemoveField(
            model_name='timeline',
            name='count_of_users',
        ),
        migrations.AlterField(
            model_name='timeline',
            name='publication',
            field=models.ForeignKey(null=True, related_name='publication_to_timeline', to='publications.Publication'),
        ),
    ]
