# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('user_profile', '0064_authdevices'),
    ]

    operations = [
        migrations.RenameField(
            model_name='authdevices',
            old_name='browser_toke',
            new_name='browser_token',
        ),
    ]
