# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-09 20:41
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('photologue', '0019_photo_thumbnail'),
        ('publications', '0033_publicationgroup'),
    ]

    operations = [
        migrations.CreateModel(
            name='PublicationPhoto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='publicationimages', verbose_name='Image')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('board_photo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='board_photo', to='photologue.Photo')),
                ('tags', taggit.managers.TaggableManager(blank=True, help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags')),
            ],
            options={
                'abstract': False,
                'ordering': ('-created',),
            },
        ),
        migrations.AlterModelOptions(
            name='publicationgroup',
            options={'ordering': ('-created',)},
        ),
        migrations.AddField(
            model_name='publicationgroup',
            name='author',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='publicationgroup',
            name='content',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='publicationgroup',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='publicationgroup',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='publicationimages', verbose_name='Image'),
        ),
        migrations.AddField(
            model_name='publicationgroup',
            name='tags',
            field=taggit.managers.TaggableManager(blank=True, help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
        migrations.AlterField(
            model_name='publication',
            name='author',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='publication',
            name='content',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='publication',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
