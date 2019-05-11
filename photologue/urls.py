from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from .views import (
    PhotoDetailView,
    photo_list,
    delete_photo,
    edit_photo,
    upload_zip_form,
    upload_photo,
    collection_list,
    upload_video,
    VideoDetailView,
    delete_video,
    edit_video,
)

"""NOTE: the url names are changing. In the long term, I want to remove the 'pl-'
prefix on all urls, and instead rely on an application namespace 'photologue'.

At the same time, I want to change some URL patterns, e.g. for pagination. Changing the urls
twice within a few releases, could be confusing, so instead I am updating URLs bit by bit.

The new style will coexist with the existing 'pl-' prefix for a couple of releases.

"""
app_name = "photologue"

urlpatterns = [
    # TODO: Permitir filtrar por año, mes... (descomentar y mejorar views)
    # url(r'^multimedia/(?P<year>\d{4})/(?P<month>[0-9]{2})/(?P<day>\w{1,2})/(?P<slug>[\-\d\w]+)/$',
    #     PhotoDateDetailView.as_view(month_format='%m'),
    #     name='photo-detail'),
    # url(r'^multimedia/(?P<year>\d{4})/(?P<month>[0-9]{2})/(?P<day>\w{1,2})/$',
    #     PhotoDayArchiveView.as_view(month_format='%m'),
    #     name='photo-archive-day'),
    # url(r'^multimedia/(?P<year>\d{4})/(?P<month>[0-9]{2})/$',
    #     PhotoMonthArchiveView.as_view(month_format='%m'),
    #     name='photo-archive-month'),
    # url(r'^multimedia/(?P<year>\d{4})/$',
    #     PhotoYearArchiveView.as_view(),
    #     name='pl-photo-archive-year'),
    # url(r'^multimedia/$',
    #     PhotoArchiveIndexView.as_view(),
    #     name='pl-photo-archive'),
    url(
        r"^multimedia/(?P<username>[\w-]+)/photo/(?P<slug>[\-\d\w]+)/$",
        PhotoDetailView.as_view(),
        name="pl-photo",
    ),
    url(
        r"^multimedia/(?P<username>[\w-]+)/video/(?P<slug>[\-\d\w]+)/$",
        VideoDetailView.as_view(),
        name="pl-video",
    ),
    url(r"^delete/photo/$", delete_photo, name="delete-photo"),
    url(r"^delete/video/$", delete_video, name="delete-video"),
    url(
        r"^edit/photo/(?P<photo_id>\d+)/$",
        require_POST(login_required(edit_photo)),
        name="edit-photo",
    ),
    url(
        r"^edit/video/(?P<video_id>\d+)/$", require_POST(edit_video), name="edit-video"
    ),
    url(
        r"^submit_zip/$",
        require_POST(login_required(upload_zip_form)),
        name="upload-zip",
    ),
    url(
        r"^submit_photo/$",
        require_POST(login_required(upload_photo)),
        name="upload-photo",
    ),
    url(
        r"^submit_video/$",
        require_POST(login_required(upload_video)),
        name="upload-video",
    ),
    url(
        r"^multimedia/collection/by(?P<username>[\w-]+)/(?P<tag_slug>[\w-]+)/$",
        collection_list,
        name="collection-list",
    ),
    url(r"^multimedia/(?P<username>[\w-]+)/$", photo_list, name="photo-list"),
]
