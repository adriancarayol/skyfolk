from django.conf.urls import url
from django.urls import path

from user_profile import interests as interests_views
from user_profile.views import base as user_profile_views

app_name = "user_profile"

urlpatterns = [
    url(
        r"^profile/(?P<username>[\w-]+)/$",
        user_profile_views.profile_view,
        name="profile",
    ),
    url(
        r"^bookmark/$",
        user_profile_views.UserLikeContent.as_view(),
        name="salad_user_content",
    ),
    # url(r'^user-search/$', user_profile_views.search),
    url(
        r"^user-search/$",
        user_profile_views.SearchView.as_view(),
        name="general-search",
    ),
    # url(r'^follow/by_affinity/$', login_required(
    #     user_profile_views.FollowingByAffinityList.as_view()),
    #     name='follow-by-affinity'),
    # url(r'^followers/by_affinity/$', login_required(
    #     user_profile_views.FollowersByAffinityList.as_view()),
    #     name='followers-by-affinity'),
    # url(r'^user-search/(?P<option>[\w]*)/$', user_profile_views.search),
    url(
        r"^user-search/(?P<option>[\w]*)/$",
        user_profile_views.SearchView.as_view(),
        name="category-search",
    ),
    # URL CONFIG PROFILE USER
    url(r"^config/profile/$", user_profile_views.config_profile, name="config_profile"),
    # URL CHANGE PRIVACITY
    url(r"^config/privacity/$", user_profile_views.config_privacity),
    # DESACTIVAR CUENTA DE SKYFOLK
    url(r"^config/delete_account/$", user_profile_views.custom_delete_account),
    # Lista de bloqueados
    url(r"^config/blocked/$", user_profile_views.config_blocked),
    url(r"^like_profile/$", user_profile_views.like_profile, name="like_profile"),
    url(
        r"^following/(?P<username>[\w-]+)/$",
        user_profile_views.following,
        name="following_profile_list",
    ),
    url(r"^followers/(?P<username>[\w-]+)/$", user_profile_views.followers),
    url(
        r"^respond_friend_request/$",
        user_profile_views.respond_friend_request,
        name="respond_friend_request",
    ),
    url(r"^request_friend/$", user_profile_views.request_friend, name="request_friend"),
    url(
        r"^remove_relationship/$",
        user_profile_views.remove_relationship,
        name="remove_relationship",
    ),
    url(r"^remove_blocked/$", user_profile_views.remove_blocked),
    url(r"^remove_request_follow/$", user_profile_views.remove_request_follow),
    url(r"^add_friend_by_pin/$", user_profile_views.add_friend_by_username_or_pin),
    url(r"^bloq_user/$", user_profile_views.bloq_user, name="bloq_user"),
    url(
        r"^accounts/password/change/confirmation",
        user_profile_views.changepass_confirmation,
    ),
    # URL CHANGE PASSWORD
    url(r"^config/password/change/$", user_profile_views.custom_password_change),
    # MANAGE EMAILS
    url(r"^config/email/$", user_profile_views.custom_email, name="account_email"),
    url(
        r"^config/password/done/$",
        user_profile_views.password_done,
        name="account_done_password",
    ),
    url(
        r"^config/notifications/$",
        user_profile_views.NotificationSettingsView.as_view(),
        name="account_notifications",
    ),
    url(
        r"^config/interests/$",
        user_profile_views.InterestsView.as_view(),
        name="account_interests",
    ),
    url(
        r"^config/affinity/$",
        user_profile_views.AffinityView.as_view(),
        name="account_affinity",
    ),
    # Página de bienvenida a nuevos usuarios.
    url(
        r"^welcome/(?P<username>[\w-]+)/$",
        user_profile_views.welcome_view,
        name="welcome",
    ),
    # Página de bienvenida, paso 1.
    url(r"^topics/$", user_profile_views.welcome_step_1, name="welcome_step_1"),
    # Establece si el usuario es la primera vez que se loguea
    url(
        r"^set_first_login/$",
        user_profile_views.set_first_Login,
        name="set_first_login",
    ),
    # Recomendacion de usuarios dependiendo de intereses
    url(
        r"^recommendations/$",
        user_profile_views.recommendation_users,
        name="reccomendation_users",
    ),
    # Lista de usuarios que han dado like al perfil <<username>>
    url(
        r"^likes/(?P<username>[\w-]+)/$", user_profile_views.like_list, name="like_list"
    ),
    url(
        r"^recommendations/users/$",
        user_profile_views.recommendation_real_time,
        name="recommendation_users",
    ),
    url(
        r"^search/autocomplete/$", user_profile_views.autocomplete, name="autocomplete"
    ),
    # Interest VIEWS
    url(
        r"^profile/(?P<username>[\w-]+)/interests/$",
        interests_views.ProfileInterests.as_view(),
        name="json_profile_interests",
    ),
    path("interest/<int:id>/", interests_views.delete_interest, name="delete_interest"),
]
