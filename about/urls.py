from django.conf.urls import url

from about.views import EntryListView

urlpatterns = [
    url(r'^blog/$', EntryListView.as_view(),
        name='blog'),
]
