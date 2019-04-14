# Generated by Django 2.1.1 on 2019-03-10 11:49

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("awards", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(model_name="userrank", name="user"),
        migrations.AddField(
            model_name="userrank",
            name="users",
            field=models.ManyToManyField(
                to=settings.AUTH_USER_MODEL, verbose_name="users"
            ),
        ),
    ]
