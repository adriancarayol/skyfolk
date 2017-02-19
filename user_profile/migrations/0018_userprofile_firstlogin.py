# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('user_profile', '0017_userprofile_ultimosusuariosvisitados'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='firstLogin',
            field=models.BooleanField(default=False),
        ),
    ]
