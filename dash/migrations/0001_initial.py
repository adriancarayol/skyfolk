# Generated by Django 2.1.1 on 2018-09-18 18:57

import dash.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0009_alter_user_last_name_max_length"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="DashboardEntry",
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
                ("layout_uid", models.CharField(max_length=25, verbose_name="Layout")),
                (
                    "placeholder_uid",
                    models.CharField(max_length=255, verbose_name="Placeholder"),
                ),
                (
                    "plugin_uid",
                    models.CharField(max_length=255, verbose_name="Plugin name"),
                ),
                (
                    "plugin_data",
                    models.TextField(blank=True, null=True, verbose_name="Plugin data"),
                ),
                (
                    "position",
                    models.PositiveIntegerField(
                        blank=True, null=True, verbose_name="Position"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="User",
                    ),
                ),
            ],
            options={
                "verbose_name": "Dashboard entry",
                "verbose_name_plural": "Dashboard entries",
                "permissions": (("copy_entry", "Copy Entry"),),
            },
        ),
        migrations.CreateModel(
            name="DashboardPlugin",
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
                    "plugin_uid",
                    models.CharField(
                        editable=False,
                        max_length=255,
                        unique=True,
                        verbose_name="Plugin UID",
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True, to="auth.Group", verbose_name="Group"
                    ),
                ),
                (
                    "users",
                    models.ManyToManyField(
                        blank=True, to=settings.AUTH_USER_MODEL, verbose_name="User"
                    ),
                ),
            ],
            options={
                "verbose_name": "Dashboard plugin",
                "verbose_name_plural": "Dashboard plugins",
            },
        ),
        migrations.CreateModel(
            name="DashboardSettings",
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
                ("layout_uid", models.CharField(max_length=25, verbose_name="Layout")),
                ("title", models.CharField(max_length=255, verbose_name="Title")),
                (
                    "allow_different_layouts",
                    models.BooleanField(
                        default=True,
                        help_text="Allows you to use different layouts for each workspace.",
                        verbose_name="Allow different layouts per workspace?",
                    ),
                ),
                (
                    "is_public",
                    models.BooleanField(
                        default=False,
                        help_text="Makes your dashboard to be visible to the public. Visibility of workspaces could be adjust separately for each workspace, however setting your dashboard to be visible to public, makes your default workspace visible to public too.",
                        verbose_name="Is public?",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="User",
                    ),
                ),
            ],
            options={
                "verbose_name": "Dashboard settings",
                "verbose_name_plural": "Dashboard settings",
            },
        ),
        migrations.CreateModel(
            name="DashboardWorkspace",
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
                ("layout_uid", models.CharField(max_length=25, verbose_name="Layout")),
                ("name", models.CharField(max_length=255, verbose_name="Name")),
                (
                    "slug",
                    django_extensions.db.fields.AutoSlugField(
                        blank=True,
                        editable=False,
                        populate_from="name",
                        unique=True,
                        verbose_name="Slug",
                    ),
                ),
                (
                    "position",
                    dash.fields.OrderField(
                        blank=True, null=True, verbose_name="Position"
                    ),
                ),
                (
                    "is_public",
                    models.BooleanField(
                        default=False,
                        help_text="Makes your workspace to be visible to the public.",
                        verbose_name="Is public?",
                    ),
                ),
                (
                    "is_clonable",
                    models.BooleanField(
                        default=False,
                        help_text="Makes your workspace to be cloneable by other users.",
                        verbose_name="Is cloneable?",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="User",
                    ),
                ),
            ],
            options={
                "verbose_name": "Dashboard workspace",
                "verbose_name_plural": "Dashboard workspaces",
                "permissions": (("view_workspace", "View workspace"),),
            },
        ),
        migrations.AddField(
            model_name="dashboardentry",
            name="workspace",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="dash.DashboardWorkspace",
                verbose_name="Workspace",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="dashboardworkspace",
            unique_together={("user", "slug"), ("user", "name")},
        ),
    ]
