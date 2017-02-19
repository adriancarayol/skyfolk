# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('user_profile', '0053_remove_userprofile_need_follow_confirmation'),
    ]

    operations = [
        migrations.CreateModel(
            name='LastUserVisit',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('affinity', models.IntegerField(default=0, verbose_name='affinity')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('emitter', models.ForeignKey(related_name='from_profile', to='user_profile.UserProfile')),
                ('receiver', models.ForeignKey(related_name='to_profile', to='user_profile.UserProfile')),
            ],
            options={
                'get_latest_by': 'created',
            },
        ),
    ]
