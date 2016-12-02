# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('user_groups', '0011_usergroups_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='rolusergroup',
            name='rol',
            field=models.CharField(default='A', max_length=1, choices=[('A', 'Admin'), ('M', 'Mod'), ('N', 'Normal')]),
        ),
        migrations.AddField(
            model_name='rolusergroup',
            name='user',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True, related_name='rol_user'),
        ),
        migrations.AlterField(
            model_name='usergroups',
            name='users',
            field=models.ManyToManyField(to='user_groups.RolUserGroup', blank=True, related_name='users_in_group'),
        ),
    ]
