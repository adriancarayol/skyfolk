# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('user_groups', '0012_auto_20161202_1908'),
    ]

    operations = [
        migrations.CreateModel(
            name='LikeGroup',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('from_like', models.ForeignKey(related_name='from_likegroup', to='user_groups.UserGroups')),
                ('to_like', models.ForeignKey(related_name='to_likegroup', to='user_groups.UserGroups')),
            ],
            options={
                'get_latest_by': 'created',
            },
        ),
        migrations.AddField(
            model_name='usergroups',
            name='likes',
            field=models.ManyToManyField(related_name='likesToGroup', through='user_groups.LikeGroup',
                                         to='user_groups.UserGroups'),
        ),
        migrations.AlterUniqueTogether(
            name='likegroup',
            unique_together=set([('from_like', 'to_like')]),
        ),
    ]
