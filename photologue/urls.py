from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import RedirectView

from .views import PhotoDetailView, \
    PhotoArchiveIndexView, PhotoDateDetailView, PhotoDayArchiveView, \
    PhotoYearArchiveView, PhotoMonthArchiveView, \
    GalleryDateDetailOldView, \
    GalleryDayArchiveOldView, GalleryMonthArchiveOldView, PhotoDateDetailOldView, \
    PhotoDayArchiveOldView, PhotoMonthArchiveOldView, photo_list, delete_photo, edit_photo, \
    upload_zip_form, upload_photo, collection_list

"""NOTE: the url names are changing. In the long term, I want to remove the 'pl-'
prefix on all urls, and instead rely on an application namespace 'photologue'.

At the same time, I want to change some URL patterns, e.g. for pagination. Changing the urls
twice within a few releases, could be confusing, so instead I am updating URLs bit by bit.

The new style will coexist with the existing 'pl-' prefix for a couple of releases.

"""

urlpatterns = [
    url(r'^$',
        RedirectView.as_view(
            url=reverse_lazy('photologue:pl-publications_gallery-archive'), permanent=True),
        name='pl-photologue-root'),
    url(r'^photo/(?P<year>\d{4})/(?P<month>[0-9]{2})/(?P<day>\w{1,2})/(?P<slug>[\-\d\w]+)/$',
        PhotoDateDetailView.as_view(month_format='%m'),
        name='photo-detail'),
    url(r'^photo/(?P<year>\d{4})/(?P<month>[0-9]{2})/(?P<day>\w{1,2})/$',
        PhotoDayArchiveView.as_view(month_format='%m'),
        name='photo-archive-day'),
    url(r'^photo/(?P<year>\d{4})/(?P<month>[0-9]{2})/$',
        PhotoMonthArchiveView.as_view(month_format='%m'),
        name='photo-archive-month'),
    url(r'^photo/(?P<year>\d{4})/$',
        PhotoYearArchiveView.as_view(),
        name='pl-photo-archive-year'),
    url(r'^photo/$',
        PhotoArchiveIndexView.as_view(),
        name='pl-photo-archive'),

    url(r'^photo/(?P<slug>[\-\d\w]+)/$',
        PhotoDetailView.as_view(),
        name='pl-photo'),

    url(r'^delete/photo/$', login_required(delete_photo), name='delete-photo'),

    url(r'^edit/photo/(?P<photo_id>\d+)/$', require_POST(login_required(edit_photo)), name='edit-photo'),

    url(r'^submit_zip/$', require_POST(login_required(upload_zip_form)), name='upload-zip'),

    url(r'^submit_photo/$', require_POST(login_required(upload_photo)), name='upload-photo'),

    url(r'^multimedia/collection/by(?P<username>[\w-]+)/(?P<tagname>[^,]+)/$', collection_list, name='collection-list'),

    url(r'^multimedia/(?P<username>[\w-]+)/$',
        photo_list,
        name='photo-list'),

    # Deprecated URLs.
    url(r'^publications_gallery/(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/(?P<slug>[\-\d\w]+)/$',
        GalleryDateDetailOldView.as_view(),
        name='pl-publications_gallery-detail'),
    url(r'^publications_gallery/(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/$',
        GalleryDayArchiveOldView.as_view(),
        name='pl-publications_gallery-archive-day'),
    url(r'^publications_gallery/(?P<year>\d{4})/(?P<month>[a-z]{3})/$',
        GalleryMonthArchiveOldView.as_view(),
        name='pl-publications_gallery-archive-month'),
    url(r'^photo/(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/(?P<slug>[\-\d\w]+)/$',
        PhotoDateDetailOldView.as_view(),
        name='pl-photo-detail'),
    url(r'^photo/(?P<year>\d{4})/(?P<month>[a-z]{3})/(?P<day>\w{1,2})/$',
        PhotoDayArchiveOldView.as_view(),
        name='pl-photo-archive-day'),
    url(r'^photo/(?P<year>\d{4})/(?P<month>[a-z]{3})/$',
        PhotoMonthArchiveOldView.as_view(),
        name='pl-photo-archive-month'),

]
