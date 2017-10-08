# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-12 23:06
from __future__ import unicode_literals

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='LikeGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('from_like', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='from_likegroup', to=settings.AUTH_USER_MODEL)),
                ('to_like', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='to_likegroup', to='auth.Group')),
            ],
            options={
                'get_latest_by': 'created',
            },
        ),
        migrations.CreateModel(
            name='RolUserGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rol', models.CharField(choices=[('A', 'Admin'), ('M', 'Mod'), ('N', 'Normal')], default='A', max_length=1)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rol_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='likegroup',
            unique_together=set([('from_like', 'to_like')]),
        ),
    ]
