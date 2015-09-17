# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import user_profile.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0002_publication'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('user_profile', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LikeProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Relationship',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('status', models.IntegerField(choices=[(1, 'Following'), (2, 'Blocked'), (3, 'Friend')])),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('status', models.IntegerField(choices=[(1, 'Friend')])),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('image', models.ImageField(blank=True, verbose_name='Image', null=True, upload_to=user_profile.models.uploadAvatarPath)),
                ('likeprofiles', models.ManyToManyField(related_name='likesToMe', through='user_profile.LikeProfile', to='user_profile.UserProfile')),
                ('publications', models.ManyToManyField(related_name='publications_to', through='publications.Publication', to='user_profile.UserProfile')),
                ('relationships', models.ManyToManyField(related_name='related_to', through='user_profile.Relationship', to='user_profile.UserProfile')),
                ('requests', models.ManyToManyField(related_name='requestsToMe', through='user_profile.Request', to='user_profile.UserProfile')),
                ('user', models.OneToOneField(related_name='profile', to=settings.AUTH_USER_MODEL)),
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
