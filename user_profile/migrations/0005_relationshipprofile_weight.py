# Generated by Django 2.1.1 on 2019-01-19 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("user_profile", "0004_remove_relationshipprofile_weight")]

    operations = [
        migrations.AddField(
            model_name="relationshipprofile",
            name="weight",
            field=models.PositiveIntegerField(default=0),
        )
    ]
