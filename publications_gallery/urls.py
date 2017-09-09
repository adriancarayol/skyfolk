from django.conf.urls import url

from . import views

urlpatterns = [
    # Publication for photo
    url(r'^publication_p/$', views.publication_photo_view,
        name='new_photo_publication'),
    # Vista completa del comentario
    url(r'^publication_pdetail/(?P<publication_id>\d+)/$', views.publication_detail,
        name='publication_photo_detail'),
    url(r'^publication_p/delete/$', views.delete_publication,
        name='delete_photo_publication'),
    url(r'^publication_p/add_like/$', views.add_like,
        name='add_like_photo_publication'),
    url(r'^publication_p/add_hate/$', views.add_hate,
        name='add_hate_photo_publication'),
    url(r'^publication_p/share/publication/$', views.share_publication,
        name='publication_share_photo_pub'),
    url(r'^publication_p/edit/$', views.edit_publication,
        name='publication_edit_photo_pub'),
    url(r'^publication_p/load_descendants/$', views.load_more_descendants,
        name='load_more_descenants_photo_pub'),
    url(r'^publication_p/delete/share/publication/$', views.RemoveSharedPhotoPublication.as_view(),
        name='publication_delete_share_photo_pub'),

]
