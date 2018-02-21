# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-02-18 13:20
from __future__ import unicode_literals

import django.db.models.deletion
import taggit.managers
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('publications_groups', '0001_initial'),
        ('user_groups', '0001_initial'),
        ('taggit', '0002_auto_20150616_2121'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='publicationgroup',
            name='board_group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user_groups.UserGroups'),
        ),
        migrations.AddField(
            model_name='publicationgroup',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reply_group', to='publications_groups.PublicationGroup'),
        ),
        migrations.AddField(
            model_name='publicationgroup',
            name='tags',
            field=taggit.managers.TaggableManager(blank=True, help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='publicationgroup',
            name='user_give_me_hate',
            field=models.ManyToManyField(blank=True, related_name='hates_group_publication', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='publicationgroup',
            name='user_give_me_like',
            field=models.ManyToManyField(blank=True, related_name='likes_group_publication', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='extragroupcontent',
            name='publication',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='group_extra_content', to='publications_groups.PublicationGroup'),
        ),
        migrations.AlterUniqueTogether(
            name='publicationgroup',
            unique_together=set([('board_group', 'id')]),
        ),
    ]
