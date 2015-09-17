# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0002_auto_20150917_0421'),
        ('publications', '0002_publication'),
    ]

    operations = [
        migrations.AddField(
            model_name='publication',
            name='profile',
            field=models.ForeignKey(related_name='to_publication', to='user_profile.UserProfile'),
        ),
        migrations.AddField(
            model_name='publication',
            name='writer',
            field=models.ForeignKey(related_name='from_publication', to='user_profile.UserProfile'),
        ),
    ]
