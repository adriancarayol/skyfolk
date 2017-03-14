# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-13 19:46
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('publications', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventTimeline',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_type', models.IntegerField(choices=[(1, 'publication'), (2, 'new_relation'), (3, 'notice'), (4, 'relevant'), (5, 'imagen')], default=1)),
                ('content', models.CharField(blank=True, max_length=255, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='owner_event', to=settings.AUTH_USER_MODEL)),
                ('profile', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='profile_event', to=settings.AUTH_USER_MODEL)),
                ('publication', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='publication', to='publications.Publication')),
            ],
        ),
        migrations.CreateModel(
            name='Timeline',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('events', models.ManyToManyField(related_name='events', to='timeline.EventTimeline')),
                ('timeline_owner', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='owner_timeline', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
