# Generated by Django 2.1.1 on 2019-01-19 12:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0003_relationshipprofile_weight'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='relationshipprofile',
            name='weight',
        ),
    ]
