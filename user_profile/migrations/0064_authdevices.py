# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0063_auto_20161031_2327'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuthDevices',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('browser_toke', models.CharField(max_length=1024)),
                ('user_profile', models.ForeignKey(related_name='device_to_profile', to='user_profile.UserProfile')),
            ],
        ),
    ]
