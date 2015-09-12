# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import user_profile.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LikeProfile',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Relationship',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('status', models.IntegerField(choices=[(1, 'Following'), (2, 'Blocked'), (3, 'Friend')])),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('status', models.IntegerField(choices=[(1, 'Friend')])),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('image', models.ImageField(blank=True, upload_to=user_profile.models.uploadAvatarPath, null=True, verbose_name='Image')),
                ('likeprofiles', models.ManyToManyField(to='user_profile.UserProfile', through='user_profile.LikeProfile', related_name='likesToMe')),
                ('publications', models.ManyToManyField(to='user_profile.UserProfile', through='publications.Publication', related_name='publications_to')),
                ('relationships', models.ManyToManyField(to='user_profile.UserProfile', through='user_profile.Relationship', related_name='related_to')),
                ('requests', models.ManyToManyField(to='user_profile.UserProfile', through='user_profile.Request', related_name='requestsToMe')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL, related_name='profile')),
            ],
            options={
                'db_table': 'user_profile',
            },
        ),
        migrations.AddField(
            model_name='request',
            name='emitter',
            field=models.ForeignKey(related_name='from_request', to='user_profile.UserProfile'),
        ),
        migrations.AddField(
            model_name='request',
            name='receiver',
            field=models.ForeignKey(related_name='to_request', to='user_profile.UserProfile'),
        ),
        migrations.AddField(
            model_name='relationship',
            name='from_person',
            field=models.ForeignKey(related_name='from_people', to='user_profile.UserProfile'),
        ),
        migrations.AddField(
            model_name='relationship',
            name='to_person',
            field=models.ForeignKey(related_name='to_people', to='user_profile.UserProfile'),
        ),
        migrations.AddField(
            model_name='likeprofile',
            name='from_like',
            field=models.ForeignKey(related_name='from_likeprofile', to='user_profile.UserProfile'),
        ),
        migrations.AddField(
            model_name='likeprofile',
            name='to_like',
            field=models.ForeignKey(related_name='to_likeprofile', to='user_profile.UserProfile'),
        ),
        migrations.AlterUniqueTogether(
            name='request',
            unique_together=set([('emitter', 'receiver', 'status')]),
        ),
        migrations.AlterUniqueTogether(
            name='relationship',
            unique_together=set([('from_person', 'to_person', 'status')]),
        ),
        migrations.AlterUniqueTogether(
            name='likeprofile',
            unique_together=set([('from_like', 'to_like')]),
        ),
    ]
