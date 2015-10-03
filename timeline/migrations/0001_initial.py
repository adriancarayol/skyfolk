# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0013_userprofile_backimage'),
    ]

    operations = [
        migrations.CreateModel(
            name='Timeline',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('content', models.TextField()),
                ('insertion_date', models.DateField(auto_now_add=True)),
                ('author', models.ForeignKey(to='user_profile.UserProfile', related_name='from_author')),
            ],
        ),
    ]
