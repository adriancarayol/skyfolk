# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('publications', '0024_auto_20160317_1908'),
    ]

    operations = [
        migrations.AddField(
            model_name='publication',
            name='hates',
            field=models.IntegerField(default=0, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='publication',
            name='user_give_me_hate',
            field=models.ManyToManyField(related_name='hates_me', to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AlterField(
            model_name='publication',
            name='user_give_me_like',
            field=models.ManyToManyField(related_name='likes_me', to=settings.AUTH_USER_MODEL, blank=True),
        ),
    ]
