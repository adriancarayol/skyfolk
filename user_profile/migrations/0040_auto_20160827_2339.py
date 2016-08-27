# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0039_auto_20160827_2338'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='galleryextended',
            name='owner',
        ),
        migrations.RemoveField(
            model_name='photoextended',
            name='owner',
        ),
    ]
