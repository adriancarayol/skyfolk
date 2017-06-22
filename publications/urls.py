from django.conf.urls import url, include

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
    url(r'^publication/(?P<publication_id>\d+)/$', publications_views.publication_detail,
        name='publication_detail'),
    url(r'^publication/edit/$', publications_views.edit_publication,
        name='publication_edit'),
    url(r'^publication/load/more/', publications_views.load_more_comments,
        name='publication_load_more'),
    url(r'^publication/load/skyline/', publications_views.load_more_skyline,
        name='publication_load_skyline'),
    url(r'^publication/share/publication/', publications_views.share_publication,
        name='publication_share_pub'),

    # Publicaciones en imagenes de la galeria
    url(r'^', include('publications_gallery.urls')),
]
