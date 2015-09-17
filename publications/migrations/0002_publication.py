# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('publications', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Publication',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('content', models.TextField()),
                ('image', models.ImageField(blank=True, verbose_name='Image', null=True, upload_to='publicationimages')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('is_response_from', models.ForeignKey(related_name='responses', null=True, to='publications.Publication')),
            ],
        ),
    ]
