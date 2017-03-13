from django.conf.urls import url

from publications import views as publications_views

urlpatterns = [
    url(r'^publication/$', publications_views.publication_new_view,
        name='new_publication'),
    url(r'^publication/delete/$', publications_views.delete_publication,
        name='delete_publication'),
    # url(r'^publication/list/$', publications_views.PublicationsListView.as_view(),
    #    name='last_publication'),
    url(r'^publication/add_like/$', publications_views.add_like,
        name='add_like'),
    url(r'^publication/add_hate/$', publications_views.add_hate,
        name='add_hate'),
    # Publication for photo
    url(r'^publication_photo/$', publications_views.publication_photo_view,
        name='new_photo_publication'),
    url(r'^publication/(?P<publication_id>\d+)/$', publications_views.publication_detail,
        name='publication_detail'),
    url(r'^publication/edit/$', publications_views.edit_publication,
        name='publication_edit'),
]
