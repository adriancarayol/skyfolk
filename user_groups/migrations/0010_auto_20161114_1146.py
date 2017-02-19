# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('user_groups', '0009_auto_20161114_1145'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usergroups',
            name='privacity',
            field=models.BooleanField(default=True,
                                      help_text='Desactiva esta casilla si quieres que el grupo sea privado.'),
        ),
    ]
