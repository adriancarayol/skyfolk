# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('user_profile', '0054_lastuservisit'),
    ]

    operations = [
        migrations.CreateModel(
            name='FavouriteUsers',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('affinity', models.IntegerField(verbose_name='affinity', default=0)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('emitter', models.ForeignKey(related_name='from_profile_fav', to='user_profile.UserProfile')),
                ('receiver', models.ForeignKey(related_name='to_profile_fav', to='user_profile.UserProfile')),
            ],
            options={
                'get_latest_by': 'created',
            },
        ),
        migrations.CreateModel(
            name='UserProfileManager',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.AlterField(
            model_name='lastuservisit',
            name='emitter',
            field=models.ForeignKey(related_name='from_profile_affinity', to='user_profile.UserProfile'),
        ),
        migrations.AlterField(
            model_name='lastuservisit',
            name='receiver',
            field=models.ForeignKey(related_name='to_profile_affinity', to='user_profile.UserProfile'),
        ),
    ]
