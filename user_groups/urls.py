from django.conf.urls import url

from user_groups import views as user_groups_views

urlpatterns = [
    # url(r'^group/(?P<group_name>[\w-]+)/$', 'user_groups.views.user_group_create', name='group'),
    url(r'^create_group/$', user_groups_views.user_group_create,
        name='create_group'),
    # listado de grupos creados
    url(r'^groups/$', user_groups_views.UserGroupList.as_view(),
        name='list-group'),
    # Perfil de un grupo
    url(r'^group/(?P<groupname>[\w-]+)/$', user_groups_views.group_profile,
        name='group-profile'),
    # Para seguir a un grupo
    url(r'^follow_group/$', user_groups_views.follow_group,
        name='follow-group'),
    # Para dejar de seguir a un grupo
    url(r'^unfollow_group/$', user_groups_views.unfollow_group,
        name='follow-group'),
    # Dar me gusta a un grupo
    url(r'^like_group/$', user_groups_views.like_group,
        name='like-group'),
    # Seguidores de un grupo.
    url(r'^users/(?P<groupname>[\w-]+)/$',
        user_groups_views.FollowersGroup.as_view()),
    url(r'^glikes/(?P<groupname>[\w-]+)/$',
        user_groups_views.likes_group),
    url(r'^respond_group_request/$',
        user_groups_views.respond_group_request),
    url(r'^remove_group_request/$',
        user_groups_views.remove_group_request),
    url(r'^kick_member/$',
        user_groups_views.kick_member),
    url(r'^groups/profile/(?P<user_id>\d+)/$', user_groups_views.list_group_profile,
        name='list_group_profile'),
    url(r'^groups/create/theme/$', user_groups_views.CreateGroupThemeView.as_view(),
        name='create_group_theme'),
    url(r'^groups/like/theme/$', user_groups_views.AddLikeTheme.as_view(),
        name='like_group_theme'),
    url(r'^groups/theme/(?P<slug>[\w-]+)/$', user_groups_views.GroupThemeView.as_view(),
        name='group_theme'),
]
