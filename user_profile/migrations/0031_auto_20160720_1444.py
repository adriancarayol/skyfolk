# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('user_profile', '0030_auto_20160719_1114'),
    ]

    operations = [
        migrations.AlterField(
            model_name='request',
            name='notification',
            field=models.ForeignKey(null=True, to='notifications.Notification', related_name='request_notification'),
        ),
    ]
