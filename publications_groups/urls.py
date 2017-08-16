from django.conf.urls import url

from . import views

urlpatterns = [
    # Publication for photo
    url(r'^publication_g/$', views.publication_group_view,
        name='new_group_publication'),
]
