# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('publications', '0009_remove_publication_isactive'),
    ]

    operations = [
        migrations.AddField(
            model_name='publication',
            name='mlikes',
            field=models.IntegerField(verbose_name='likes_comment', null=True, blank=True),
        ),
    ]
