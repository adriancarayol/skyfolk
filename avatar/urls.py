from django.conf.urls import url

from avatar import views

urlpatterns = [
    url(r'^/config/add/avatar/$', views.add, name='avatar_add'),
    url(r'^/config/change/avatar/$', views.change, name='avatar_change'),
    url(r'^/config/delete/avatar/$', views.delete, name='avatar_delete'),
    url(r'^render_primary/(?P<user>[\w\d\@\.\-_]+)/(?P<size>[\d]+)/$',
        views.render_primary,
        name='avatar_render_primary'),
]
