# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('subject', models.CharField(max_length=120, verbose_name='Subject')),
                ('body', models.TextField(verbose_name='Body')),
                ('sent_at', models.DateTimeField(blank=True, null=True, verbose_name='sent at')),
                ('read_at', models.DateTimeField(blank=True, null=True, verbose_name='read at')),
                ('replied_at', models.DateTimeField(blank=True, null=True, verbose_name='replied at')),
                ('sender_deleted_at', models.DateTimeField(blank=True, null=True, verbose_name='Sender deleted at')),
                ('recipient_deleted_at', models.DateTimeField(blank=True, null=True, verbose_name='Recipient deleted at')),
                ('parent_msg', models.ForeignKey(blank=True, null=True, to='django_messages.Message', related_name='next_messages', verbose_name='Parent message')),
                ('recipient', models.ForeignKey(blank=True, null=True, to=settings.AUTH_USER_MODEL, related_name='received_messages', verbose_name='Recipient')),
                ('sender', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='sent_messages', verbose_name='Sender')),
            ],
            options={
                'verbose_name_plural': 'Messages',
                'ordering': ['-sent_at'],
                'verbose_name': 'Message',
            },
        ),
    ]
