# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import achievements.models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0022_userprofile_hiddenmenu'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='achievements',
            field=models.ManyToManyField(db_constraint=achievements.models.Achievements, to='user_profile.UserProfile'),
        ),
    ]
