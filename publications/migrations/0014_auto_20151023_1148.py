# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0013_publication_user_give_me_like'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publication',
            name='user_give_me_like',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
    ]
