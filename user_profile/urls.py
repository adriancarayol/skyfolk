from django.conf.urls import url
from .views import UserAutocomplete

urlpatterns = [
    url(r'^profile/(?P<username>[\w-]+)/$', 'user_profile.views.profile_view',
        name='profile'),
    url(r'^search/$', 'user_profile.views.search'),
    url(r'^search/(?P<option>[\w]*)/$', 'user_profile.views.search'),
    url(r'^search-advanced/$', 'user_profile.views.advanced_view',
        name='advanced_view'),
    # URL CONFIG PROFILE USER
    url(r'^config/profile/$', 'user_profile.views.config_profile',
        name="config_profile"),
    # URL CHANGE PRIVACITY
    url(r'^config/privacity/$', 'user_profile.views.config_privacity'),
    # CONSULTAR PINCODE
    url(r'^config/pincode/$', 'user_profile.views.config_pincode'),
    # DESACTIVAR CUENTA DE SKYFOLK
    url(r'^config/delete_account/$',
        'user_profile.views.custom_delete_account'),
    # Lista de bloqueados
    url(r'^config/blocked/$', 'user_profile.views.config_blocked'),
    url(r'^like_profile/$', 'user_profile.views.like_profile',
        name='like_profile'),
    url(r'^following/(?P<username>[\w-]+)/$', 'user_profile.views.following'),
    url(r'^followers/(?P<username>[\w-]+)/$', 'user_profile.views.followers'),
    url(r'^respond_friend_request/$',
        'user_profile.views.respond_friend_request',
        name='respond_friend_request'),
    # Cargar mas followers
    url(r'^load_followers/$', 'user_profile.views.load_followers'),
    # Cargar mas follows
    url(r'^load_follows/$', 'user_profile.views.load_follows'),
    url(r'^request_friend/$', 'user_profile.views.request_friend'),
    url(r'^remove_relationship/$', 'user_profile.views.remove_relationship'),
    url(r'^remove_blocked/$', 'user_profile.views.remove_blocked'),
    url(r'^remove_request_follow/$',
        'user_profile.views.remove_request_follow'),
    url(r'^add_friend_by_pin/$',
        'user_profile.views.add_friend_by_username_or_pin'),
    url(r'^bloq_user/$', 'user_profile.views.bloq_user'),
    url(r'^accounts/password/change/confirmation',
        'user_profile.views.changepass_confirmation'),
    # URL CHANGE PASSWORD
    url(r'^config/password/change/$',
        'user_profile.views.custom_password_change'),
    # MANAGE EMAILS
    url(r'^config/email/$', 'user_profile.views.custom_email',
        name='account_email'),
    url(r"^config/password/done/$", 'user_profile.views.password_done',
        name="account_done_password"),
    # Página de bienvenida a nuevos usuarios.
    url(r'^welcome/(?P<username>[\w-]+)/$', 'user_profile.views.welcome_view',
        name='welcome'),
    # Página de bienvenida, paso 1.
    url(r'^topics/$', 'user_profile.views.welcome_step_1',
        name='welcome_step_1'),
    # Establece si el usuario es la primera vez que se loguea
    url(r'^set_first_login/$', 'user_profile.views.set_first_Login',
        name='set_first_login'),
    # Recomendacion de usuarios dependiendo de intereses
    url(r'^recommendations/$', 'user_profile.views.recommendation_users',
        name='reccomendation_users'),
    # Lista de usuarios que han dado like al perfil <<username>>
    url(r'^likes/(?P<username>[\w-]+)/$', 'user_profile.views.like_list',
        name='like_list'),
]
