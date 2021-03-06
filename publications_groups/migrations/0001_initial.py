# Generated by Django 2.1.1 on 2018-09-18 18:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import embed_video.fields
import publications.utils
import publications_groups.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="ExtraGroupContent",
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
                ("title", models.CharField(default="", max_length=64)),
                ("description", models.CharField(default="", max_length=256)),
                ("image", models.URLField(blank=True, null=True)),
                ("url", models.URLField()),
                ("video", embed_video.fields.EmbedVideoField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="PublicationGroup",
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
                ("content", models.TextField(max_length=10000)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("edition_date", models.DateTimeField(blank=True, null=True)),
                ("deleted", models.BooleanField(blank=True, default=False)),
                (
                    "event_type",
                    models.IntegerField(
                        choices=[
                            (1, "publication"),
                            (2, "new_relation"),
                            (3, "link"),
                            (4, "relevant"),
                            (5, "imagen"),
                            (6, "shared"),
                        ],
                        default=1,
                    ),
                ),
                ("lft", models.PositiveIntegerField(db_index=True, editable=False)),
                ("rght", models.PositiveIntegerField(db_index=True, editable=False)),
                ("tree_id", models.PositiveIntegerField(db_index=True, editable=False)),
                ("level", models.PositiveIntegerField(db_index=True, editable=False)),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PublicationGroupImage",
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
                    "image",
                    models.ImageField(
                        upload_to=publications_groups.models.upload_image_group_publication
                    ),
                ),
                (
                    "publication",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="images",
                        to="publications_groups.PublicationGroup",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PublicationGroupVideo",
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
                    "video",
                    models.FileField(
                        upload_to=publications_groups.models.upload_video_group_publication,
                        validators=[publications.utils.validate_video],
                    ),
                ),
                (
                    "publication",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="videos",
                        to="publications_groups.PublicationGroup",
                    ),
                ),
            ],
        ),
    ]
