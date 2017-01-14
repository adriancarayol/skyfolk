from django.conf.urls import url

urlpatterns = [
    # url(r'^group/(?P<group_name>[\w-]+)/$', 'user_groups.views.user_group_create', name='group'),
    url(r'^create_group/$', 'user_groups.views.user_group_create',
        name='create_group'),
    # listado de grupos creados
    url(r'^groups/$', 'user_groups.views.group_list',
        name='list-group'),
    # Perfil de un grupo
    url(r'^group/(?P<groupname>[\w-]+)/$', 'user_groups.views.group_profile',
        name='group-profile'),
    # Para seguir a un grupo
    url(r'^follow_group/$', 'user_groups.views.follow_group',
        name='follow-group'),
    # Para dejar de seguir a un grupo
    url(r'^unfollow_group/$', 'user_groups.views.unfollow_group',
        name='follow-group'),
    # Dar me gusta a un grupo
    url(r'^like_group/$', 'user_groups.views.like_group',
        name='like-group'),
]