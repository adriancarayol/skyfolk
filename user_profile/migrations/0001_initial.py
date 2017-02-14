# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        # migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        # ('publications', '0001_initial'),
    ]

    operations = [
        # migrations.CreateModel(
        #    name='LikeProfile',
        #    fields=[
        #        ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
        #        ('created', models.DateTimeField(auto_now_add=True)),
        #    ],
        # ),
        # migrations.CreateModel(
        #    name='Relationship',
        #    fields=[
        #        ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
        #        ('status', models.IntegerField(choices=[(1, 'Following'), (2, 'Blocked'), (3, 'Friend')])),
        #        ('created', models.DateTimeField(auto_now_add=True)),
        #    ],
        # ),
        # migrations.CreateModel(
        #    name='Request',
        #    fields=[
        #        ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
        #        ('status', models.IntegerField(choices=[(1, 'Friend')])),
        #        ('created', models.DateTimeField(auto_now_add=True)),
        #    ],
        # ),
        # migrations.CreateModel(
        #    name='UserProfile',
        #    fields=[
        #        ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
        #        ('image', models.ImageField(verbose_name='Image', null=True, upload_to=user_profile.models.uploadAvatarPath, blank=True)),
        #        ('likeprofiles', models.ManyToManyField(related_name='likesToMe', to='user_profile.UserProfile', through='user_profile.LikeProfile')),
        #        ('publications', models.ManyToManyField(related_name='publications_to', to='user_profile.UserProfile', through='publications.Publication')),
        #        ('relationships', models.ManyToManyField(related_name='related_to', to='user_profile.UserProfile', through='user_profile.Relationship')),
        #        ('requests', models.ManyToManyField(related_name='requestsToMe', to='user_profile.UserProfile', through='user_profile.Request')),
        #        ('user', models.OneToOneField(related_name='profile', to=settings.AUTH_USER_MODEL)),
        #    ],
        #    options={
        #        'db_table': 'user_profile',
        #    },
        # ),
        # migrations.AddField(
        #    model_name='request',
        #    name='emitter',
        #    field=models.ForeignKey(related_name='from_request', to='user_profile.UserProfile'),
        # ),
        # migrations.AddField(
        #    model_name='request',
        #    name='receiver',
        #    field=models.ForeignKey(related_name='to_request', to='user_profile.UserProfile'),
        # ),
        # migrations.AddField(
        #    model_name='relationship',
        #    name='from_person',
        #    field=models.ForeignKey(related_name='from_people', to='user_profile.UserProfile'),
        # ),
        # migrations.AddField(
        #    model_name='relationship',
        #    name='to_person',
        #    field=models.ForeignKey(related_name='to_people', to='user_profile.UserProfile'),
        # ),
        # migrations.AddField(
        #    model_name='likeprofile',
        #    name='from_like',
        #    field=models.ForeignKey(related_name='from_likeprofile', to='user_profile.UserProfile'),
        # ),
        # migrations.AddField(
        #    model_name='likeprofile',
        #    name='to_like',
        #    field=models.ForeignKey(related_name='to_likeprofile', to='user_profile.UserProfile'),
        # ),
        # migrations.AlterUniqueTogether(
        #    name='request',
        #    unique_together=set([('emitter', 'receiver', 'status')]),
        # ),
        # migrations.AlterUniqueTogether(
        #    name='relationship',
        #    unique_together=set([('from_person', 'to_person', 'status')]),
        # ),
        # migrations.AlterUniqueTogether(
        #    name='likeprofile',
        #    unique_together=set([('from_like', 'to_like')]),
        # ),
    ]
