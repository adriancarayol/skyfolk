from django.conf.urls import url

from publications import views as publications_views

app_name = 'publications'

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
    url(r'^publication/share/publication/', publications_views.share_publication,
        name='publication_share_pub'),
    url(r'^publication/delete/share/publication/', publications_views.RemoveSharedPublication.as_view(),
        name='publication_delete_share_pub'),

    # Filtros para skyline
    url(r'^publications/filter/time/$', publications_views.publication_filter_by_time,
        name="publications_filter_time"),
    url(r'^publications/filter/like/$', publications_views.publication_filter_by_like,
        name="publications_filter_like"),
    url(r'^publications/filter/relevance/$', publications_views.publication_filter_by_relevance,
        name="publications_filter_relevance"),


]
