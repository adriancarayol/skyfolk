# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('timeline', '0016_remove_timeline_users_add_me'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='timeline',
            options={'ordering': ('-insertion_date',)},
        ),
        migrations.AddField(
            model_name='timeline',
            name='type',
            field=models.CharField(choices=[('publication', 'publication'), ('new_relation', 'new_relation')],
                                   default='publication', max_length=20),
        ),
        migrations.AddField(
            model_name='timeline',
            name='verb',
            field=models.CharField(null=True, max_length=255),
        ),
    ]
