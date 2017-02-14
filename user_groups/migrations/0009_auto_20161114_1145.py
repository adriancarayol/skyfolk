# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('user_groups', '0008_auto_20161114_1118'),
    ]

    operations = [
        migrations.CreateModel(
            name='RolUserGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.AddField(
            model_name='usergroups',
            name='privacity',
            field=models.BooleanField(default=True),
        ),
    ]
