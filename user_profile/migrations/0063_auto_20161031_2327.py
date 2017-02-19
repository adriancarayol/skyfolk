# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('user_profile', '0062_auto_20161026_2126'),
    ]

    operations = [
        migrations.CreateModel(
            name='AffinityUser',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('affinity', models.IntegerField(default=0, verbose_name='affinity')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('emitter', models.ForeignKey(to='user_profile.UserProfile', related_name='from_profile_affinity')),
                ('receiver', models.ForeignKey(to='user_profile.UserProfile', related_name='to_profile_affinity')),
            ],
            options={
                'get_latest_by': 'created',
            },
        ),
        migrations.AlterUniqueTogether(
            name='lastuservisit',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='lastuservisit',
            name='emitter',
        ),
        migrations.RemoveField(
            model_name='lastuservisit',
            name='receiver',
        ),
        migrations.DeleteModel(
            name='LastUserVisit',
        ),
        migrations.AlterUniqueTogether(
            name='affinityuser',
            unique_together=set([('emitter', 'receiver')]),
        ),
    ]
