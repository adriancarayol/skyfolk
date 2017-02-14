# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('timeline', '0002_timeline_profile'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='timeline',
            name='profile',
        ),
        migrations.AlterField(
            model_name='timeline',
            name='author',
            field=models.ForeignKey(related_name='from_timeline', to='user_profile.UserProfile'),
        ),
    ]
