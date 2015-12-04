# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0016_userprofile_timeline'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='ultimosUsuariosVisitados',
            field=models.ManyToManyField(related_name='ultimosUsuariosVisitados_rel_+', to='user_profile.UserProfile'),
        ),
    ]
