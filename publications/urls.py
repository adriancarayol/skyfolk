from django.conf.urls import url

from .views import PublicationNewView, PublicationsListView

urlpatterns = [
    url(r'^publication/$', PublicationNewView.as_view(),
        name='new_publication'),
    url(r'^publication/delete/$', 'publications.views.delete_publication',
        name='delete_publication'),
    url(r'^publication/list/$', PublicationsListView.as_view(),
        name='last_publication'),
    url(r'^publication/add_like/$', 'publications.views.add_like',
        name='add_like'),
    url(r'^publication/add_hate/$', 'publications.views.add_hate',
        name='add_hate'),
    url(r'^load_publications/$', 'publications.views.load_publications'),
]
