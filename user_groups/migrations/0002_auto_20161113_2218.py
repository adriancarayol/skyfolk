# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('user_groups', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='usergroups',
            name='owner',
            field=models.ForeignKey(related_name='group_owner', null=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='usergroups',
            name='users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, related_name='users_in_group'),
        ),
    ]
