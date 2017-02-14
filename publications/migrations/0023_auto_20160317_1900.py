# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('publications', '0022_auto_20160303_2348'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='publication',
            name='comments',
        ),
        migrations.AddField(
            model_name='publication',
            name='parent',
            field=models.ForeignKey(related_name='replies', null=True, to='publications.Publication'),
        ),
    ]
