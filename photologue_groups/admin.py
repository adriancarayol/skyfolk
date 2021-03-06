from django import forms
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.contrib import messages
from django.contrib.admin import helpers
from django.contrib.sites.models import Site
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import ungettext, ugettext_lazy as _

from .forms import UploadZipForm
from .models import PhotoGroup, VideoGroup

MULTISITE = getattr(settings, "PHOTOLOGUE_MULTISITE", False)


class PhotoAdminForm(forms.ModelForm):
    class Meta:
        model = PhotoGroup
        if MULTISITE:
            exclude = []
        else:
            exclude = ["sites"]


class PhotoAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "date_taken",
        "date_added",
        "view_count",
        "admin_thumbnail",
    )
    list_filter = ["date_added"]
    if MULTISITE:
        list_filter.append("sites")
    search_fields = ["title", "slug", "caption"]
    list_per_page = 10
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("date_taken",)
    form = PhotoAdminForm
    if MULTISITE:
        filter_horizontal = ["sites"]
    if MULTISITE:
        actions = ["add_photos_to_current_site", "remove_photos_from_current_site"]

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """ Set the current site as initial value. """
        if db_field.name == "sites":
            kwargs["initial"] = [Site.objects.get_current()]
        return super(PhotoAdmin, self).formfield_for_manytomany(
            db_field, request, **kwargs
        )

    def add_photos_to_current_site(modeladmin, request, queryset):
        current_site = Site.objects.get_current()
        current_site.photo_set.add(*queryset)
        msg = ungettext(
            "The photo has been successfully added to %(site)s",
            "The selected photos have been successfully added to %(site)s",
            len(queryset),
        ) % {"site": current_site.name}
        messages.success(request, msg)

    add_photos_to_current_site.short_description = _(
        "Add selected photos to the current site"
    )

    def remove_photos_from_current_site(modeladmin, request, queryset):
        current_site = Site.objects.get_current()
        current_site.photo_set.remove(*queryset)
        msg = ungettext(
            "The photo has been successfully removed from %(site)s",
            "The selected photos have been successfully removed from %(site)s",
            len(queryset),
        ) % {"site": current_site.name}
        messages.success(request, msg)

    remove_photos_from_current_site.short_description = _(
        "Remove selected photos from the current site"
    )

    def get_urls(self):
        urls = super(PhotoAdmin, self).get_urls()
        custom_urls = [
            url(
                r"^upload_zip/$",
                self.admin_site.admin_view(self.upload_zip),
                name="photologue_upload_zip",
            )
        ]
        return custom_urls + urls

    def upload_zip(self, request):

        context = {
            "title": _("Upload a zip archive of photos"),
            "app_label": self.model._meta.app_label,
            "opts": self.model._meta,
            "has_change_permission": self.has_change_permission(request),
        }

        # Handle form request
        if request.method == "POST":
            form = UploadZipForm(request.POST, request.FILES, request=request)
            if form.is_valid():
                form.save(request=request)
                return HttpResponseRedirect("..")
        else:
            form = UploadZipForm(request=request)
        context["form"] = form
        context["adminform"] = helpers.AdminForm(
            form, list([(None, {"fields": form.base_fields})]), {}
        )
        return render(request, "admin/photologue/photo/upload_zip.html", context)


admin.site.register(PhotoGroup, PhotoAdmin)


class VideoAdmin(admin.ModelAdmin):
    list_display = ("name", "caption", "owner")


admin.site.register(VideoGroup, VideoAdmin)
