# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('user_profile', '0022_userprofile_hiddenmenu'),
        ('publications', '0017_auto_20151118_0843'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('content', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(related_name='from_response', to='user_profile.UserProfile')),
                ('child_comments', models.ManyToManyField(to='publications.Comment')),
            ],
        ),
        migrations.AddField(
            model_name='publication',
            name='comments',
            field=models.ManyToManyField(to='publications.Comment'),
        ),
    ]
