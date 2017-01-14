# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import user_groups.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserGroups',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(unique=True, max_length=128)),
                ('description', models.CharField(max_length=1024)),
                ('created', models.DateField(auto_now_add=True)),
                ('type', models.CharField(max_length=32)),
                ('small_image', models.ImageField(verbose_name='small_image', blank=True, null=True, upload_to=user_groups.models.upload_small_group_image)),
                ('large_image', models.ImageField(verbose_name='large_image', blank=True, null=True, upload_to=user_groups.models.upload_large_group_image)),
                ('users', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
