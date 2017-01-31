# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-31 15:27
from __future__ import unicode_literals

from django.db import migrations, models
import photologue.models
import photologue.validators


class Migration(migrations.Migration):

    dependencies = [
        ('photologue', '0014_remove_gallery_owner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='image',
            field=models.ImageField(upload_to=photologue.models.get_storage_path, validators=[photologue.validators.validate_file_extension], verbose_name='image'),
        ),
    ]
