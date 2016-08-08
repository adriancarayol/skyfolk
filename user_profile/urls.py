from django.conf.urls import url


urlpatterns = [
    url(r'^setfirstLogin/', 'user_profile.views.setfirstLogin', name='setfirstLogin'),
    url(r'^profile/(?P<username>[\w-]+)/$', 'user_profile.views.profile_view', name='profile'),
    url(r'^search/$', 'user_profile.views.search'),
    url(r'^search-avanzed/$', 'user_profile.views.advanced_view', name='advanced_view'),
    url(r'^config/profile/$', 'user_profile.views.config_profile'),  # URL CONFIG PROFILE USER
    url(r'^config/privacity/$', 'user_profile.views.config_privacity'),  # URL CHANGE PRIVACITY
    url(r'^config/pincode/$', 'user_profile.views.config_pincode'),  # CONSULTAR PINCODE
    url(r'^config/delete_account/$', 'user_profile.views.custom_delete_account'),  # DESACTIVAR CUENTA DE SKYFOLK
    url(r'^config/blocked/$', 'user_profile.views.config_blocked'),  # Lista de bloqueados
    url(r'^like_profile/$', 'user_profile.views.like_profile', name='like_profile'),
    url(r'^following/(?P<username>[\w-]+)/$', 'user_profile.views.following'),
    url(r'^followers/(?P<username>[\w-]+)/$', 'user_profile.views.followers'),
    url(r'^respond_friend_request/$', 'user_profile.views.respond_friend_request', name='respond_friend_request'),
    url(r'^load_followers/$', 'user_profile.views.load_followers'), # Cargar mas followers
    url(r'^load_follows/$', 'user_profile.views.load_follows'), # Cargar mas follows
    url(r'^request_friend/$', 'user_profile.views.request_friend'),
    url(r'^remove_relationship/$', 'user_profile.views.remove_relationship'),
    url(r'^remove_blocked/$', 'user_profile.views.remove_blocked'),
    url(r'^remove_request_follow/$', 'user_profile.views.remove_request_follow'),
    url(r'^add_friend_by_pin/$', 'user_profile.views.add_friend_by_username_or_pin'),
    url(r'^bloq_user/$', 'user_profile.views.bloq_user'),
    url(r'^accounts/password/change/confirmation', 'user_profile.views.changepass_confirmation'),
    url(r'^config/password/change/$', 'user_profile.views.custom_password_change'),  # URL CHANGE PASSWORD
    url(r'^config/email/$', 'user_profile.views.custom_email', name='account_email'),  # MANAGE EMAILS
    url(r"^config/password/done/$", 'user_profile.views.password_done', name="account_done_password"),
    url(r'^welcome/(?P<username>[\w-]+)/$', 'user_profile.views.welcomeView'), # Página de bienvenida a nuevos usuarios.
    url(r'^step1/(?P<username>[\w-]+)/$', 'user_profile.views.welcomeStep1', name='welcomeStep1'), # Página de bienvenida, paso 1.
]