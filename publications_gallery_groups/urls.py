from django.conf.urls import url

from . import views

app_name = "publications_gallery_groups"

urlpatterns = [
    # Publication for photo
    url(r"^publication/$", views.publication_photo_view, name="new_photo_publication"),
    # Vista completa del comentario
    url(
        r"^publication/detail/(?P<publication_id>\d+)/$",
        views.publication_detail,
        name="publication_photo_detail",
    ),
    url(
        r"^publication/delete/$",
        views.delete_publication,
        name="delete_photo_publication",
    ),
    url(r"^publication/add_like/$", views.add_like, name="add_like_photo_publication"),
    url(r"^publication/add_hate/$", views.add_hate, name="add_hate_photo_publication"),
    url(
        r"^publication/edit/$",
        views.edit_publication,
        name="publication_edit_photo_pub",
    ),
    url(
        r"^publication/load_descendants/$",
        views.load_more_descendants,
        name="load_more_descenants_photo_pub",
    ),
    # videos
    url(
        r"^video/publication/$",
        views.publication_video_view,
        name="new_video_publication",
    ),
    url(
        r"^video/publication/detail/(?P<publication_id>\d+)/$",
        views.video_publication_detail,
        name="publication_video_detail",
    ),
    url(
        r"^video/publication/delete/$",
        views.delete_video_publication,
        name="delete_video_publication",
    ),
    url(
        r"^video/publication/add_like/$",
        views.add_video_like,
        name="add_like_video_publication",
    ),
    url(
        r"^video/publication/add_hate/$",
        views.add_video_hate,
        name="add_hate_video_publication",
    ),
    url(
        r"^video/publication/edit/$",
        views.edit_video_publication,
        name="publication_video_edit",
    ),
    url(
        r"^video/publication/load/$",
        views.load_more_video_descendants,
        name="load_more_descenants_video_pub",
    ),
]
