# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('timeline', '0014_auto_20160720_2119'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timeline',
            name='publication',
            field=models.ForeignKey(null=True, related_name='publications', to='publications.Publication'),
        ),
    ]
