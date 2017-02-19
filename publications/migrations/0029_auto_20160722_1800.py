# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('publications', '0028_publication_user_share_me'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='publication',
            name='hates',
        ),
        migrations.RemoveField(
            model_name='publication',
            name='likes',
        ),
    ]
