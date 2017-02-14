# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('user_profile', '0066_auto_20161210_1615'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='personal_pin',
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
    ]
