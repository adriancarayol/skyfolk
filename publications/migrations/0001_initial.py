# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        # ('user_profile', '__first__'),
    ]

    operations = [
        # migrations.CreateModel(
        #    name='Publication',
        #    fields=[
        #        ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
        #        ('content', models.TextField()),
        #        ('image', models.ImageField(null=True, verbose_name='Image', blank=True, upload_to='publicationimages')),
        #        ('created', models.DateTimeField(auto_now_add=True)),
        #        ('is_response_from', models.ForeignKey(null=True, to='publications.Publication', related_name='responses')),
        #        ('profile', models.ForeignKey(to='user_profile.UserProfile', related_name='to_publication')),
        #        ('writer', models.ForeignKey(to='user_profile.UserProfile', related_name='from_publication')),
        #    ],
        # ),
    ]
