# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-09 20:49
from __future__ import unicode_literals

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('publications', '0034_auto_20170209_2141'),
    ]

    operations = [
        migrations.AddField(
            model_name='publicationphoto',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                    related_name='reply_photo', to='publications.PublicationPhoto'),
        ),
        migrations.AddField(
            model_name='publicationphoto',
            name='user_give_me_like',
            field=models.ManyToManyField(blank=True, related_name='likes_photo_me', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='publicationphoto',
            name='user_share_me',
            field=models.ManyToManyField(blank=True, related_name='share_photo_me', to=settings.AUTH_USER_MODEL),
        ),
    ]
