# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('photologue', '0012_auto_20160903_1619'),
    ]

    operations = [
        migrations.AddField(
            model_name='gallery',
            name='owner',
            field=models.ForeignKey(related_name='user_gallery', to=settings.AUTH_USER_MODEL, null=True, blank=True),
        ),
    ]
