# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photologue', '0013_gallery_owner'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gallery',
            name='owner',
        ),
    ]
