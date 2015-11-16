# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0017_hashtag'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='hashtag',
            name='publicacion',
        ),
        migrations.DeleteModel(
            name='Hashtag',
        ),
    ]
