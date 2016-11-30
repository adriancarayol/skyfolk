from django.conf.urls import url

urlpatterns = [
    # url(r'^group/(?P<group_name>[\w-]+)/$', 'user_groups.views.user_group_create', name='group'),
    url(r'^create_group/$', 'user_groups.views.user_group_create',
        name='create_group'),
    # listado de grupos creados
    url(r'^groups/$', 'user_groups.views.group_list',
        name='list-group'),
]