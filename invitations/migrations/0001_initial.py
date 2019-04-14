# Generated by Django 2.1.1 on 2018-09-18 18:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="Invitation",
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
                (
                    "accepted",
                    models.BooleanField(default=False, verbose_name="accepted"),
                ),
                (
                    "key",
                    models.CharField(max_length=64, unique=True, verbose_name="key"),
                ),
                ("sent", models.DateTimeField(null=True, verbose_name="sent")),
                (
                    "email",
                    models.EmailField(
                        max_length=254, unique=True, verbose_name="e-mail address"
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="created"
                    ),
                ),
                (
                    "inviter",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"abstract": False},
        )
    ]
