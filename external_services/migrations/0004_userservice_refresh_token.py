# Generated by Django 2.1.1 on 2018-11-30 18:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("external_services", "0003_auto_20181014_1322")]

    operations = [
        migrations.AddField(
            model_name="userservice",
            name="refresh_token",
            field=models.CharField(default="", max_length=255),
        )
    ]
