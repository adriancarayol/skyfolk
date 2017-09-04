from django.conf.urls import url

from . import views

urlpatterns = [
    # Publication for photo
    url(r'^publication_g/$', views.publication_group_view,
        name='new_group_publication'),
    url(r'^publication/group/delete/$', views.delete_publication,
        name='delete_group_publication'),
    url(r'^publication/group/add_like/$', views.AddPublicationLike.as_view(),
        name='add_like_group_publication'),
    url(r'^publication/group/add_hate/$', views.AddPublicationHate.as_view(),
        name='add_hate_group_publication'),
]
