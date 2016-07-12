# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0008_notification_actor_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='level',
            field=models.CharField(max_length=20, default='info', choices=[('success', 'success'), ('info', 'info'), ('warning', 'warning'), ('error', 'error'), ('friendrequest', 'friendrequest')]),
        ),
    ]
