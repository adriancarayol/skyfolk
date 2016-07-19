# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0029_request_notification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='request',
            name='notification',
            field=models.ForeignKey(related_name='request_notification', to='notifications.Notification'),
        ),
    ]
