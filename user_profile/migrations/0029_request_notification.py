# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('notifications', '0009_auto_20160712_2214'),
        ('user_profile', '0028_auto_20160713_2028'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='notification',
            field=models.ForeignKey(to='notifications.Notification', null=True, related_name='request_notification'),
        ),
    ]
