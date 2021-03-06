# Generated by Django 2.1.1 on 2018-09-18 18:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import embed_video.fields
import publications.utils
import publications_gallery_groups.models
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("taggit", "0002_auto_20150616_2121"),
        ("photologue_groups", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ExtraContentPubPhoto",
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
            name="ExtraContentPubVideo",
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
            name="PublicationGroupMediaPhoto",
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
                (
                    "board_photo",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="board_group_multimedia_photo",
                        to="photologue_groups.PhotoGroup",
                    ),
                ),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="group_multimedia_reply_photo",
                        to="publications_gallery_groups.PublicationGroupMediaPhoto",
                    ),
                ),
                (
                    "tags",
                    taggit.managers.TaggableManager(
                        blank=True,
                        help_text="A comma-separated list of tags.",
                        through="taggit.TaggedItem",
                        to="taggit.Tag",
                        verbose_name="Tags",
                    ),
                ),
                (
                    "user_give_me_hate",
                    models.ManyToManyField(
                        blank=True,
                        related_name="hate_group_multimedia_photo_me",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "user_give_me_like",
                    models.ManyToManyField(
                        blank=True,
                        related_name="likes_group_multimedia_photo_me",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="PublicationGroupMediaVideo",
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
                (
                    "board_video",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="board_group_multimedia_video",
                        to="photologue_groups.VideoGroup",
                    ),
                ),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="roup_multimedia_reply_photo",
                        to="publications_gallery_groups.PublicationGroupMediaVideo",
                    ),
                ),
                (
                    "tags",
                    taggit.managers.TaggableManager(
                        blank=True,
                        help_text="A comma-separated list of tags.",
                        through="taggit.TaggedItem",
                        to="taggit.Tag",
                        verbose_name="Tags",
                    ),
                ),
                (
                    "user_give_me_hate",
                    models.ManyToManyField(
                        blank=True,
                        related_name="hate_group_multimedia_video_me",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "user_give_me_like",
                    models.ManyToManyField(
                        blank=True,
                        related_name="likes_group_multimedia_video_me",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="PublicationPhotoImage",
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
                        upload_to=publications_gallery_groups.models.upload_image_photo_publication
                    ),
                ),
                (
                    "publication",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="images",
                        to="publications_gallery_groups.PublicationGroupMediaPhoto",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PublicationPhotoVideo",
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
                        upload_to=publications_gallery_groups.models.upload_video_photo_publication,
                        validators=[publications.utils.validate_video],
                    ),
                ),
                (
                    "publication",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="videos",
                        to="publications_gallery_groups.PublicationGroupMediaPhoto",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PublicationVideoImage",
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
                        upload_to=publications_gallery_groups.models.upload_image_photo_publication
                    ),
                ),
                (
                    "publication",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="images",
                        to="publications_gallery_groups.PublicationGroupMediaVideo",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PublicationVideoVideo",
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
                        upload_to=publications_gallery_groups.models.upload_video_photo_publication,
                        validators=[publications.utils.validate_video],
                    ),
                ),
                (
                    "publication",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="videos",
                        to="publications_gallery_groups.PublicationGroupMediaVideo",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="extracontentpubvideo",
            name="publication",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="publication_group_multimedia_video_extra_content",
                to="publications_gallery_groups.PublicationGroupMediaVideo",
            ),
        ),
        migrations.AddField(
            model_name="extracontentpubphoto",
            name="publication",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="publication_group_multimedia_photo_extra_content",
                to="publications_gallery_groups.PublicationGroupMediaPhoto",
            ),
        ),
    ]
