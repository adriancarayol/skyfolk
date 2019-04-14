# Generated by Django 2.1.1 on 2018-09-18 18:57

import avatar.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="Avatar",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("primary", models.BooleanField(default=False, verbose_name="primero")),
                ("avatar", avatar.models.AvatarField()),
                (
                    "date_uploaded",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="uploaded at"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="usuario",
                    ),
                ),
            ],
            options={"verbose_name": "avatar", "verbose_name_plural": "avatars"},
        )
    ]
