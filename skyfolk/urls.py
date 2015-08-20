#####


from django.conf.urls import patterns, include, url
from django.contrib import admin
from rest_framework import viewsets, routers
from rest_framework import routers
from api import views
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns, static
from user_profile import views as user_profile_views
from about.views import about
from market.views import market_inicio
from relaciones.views import relaciones_user

admin.autodiscover()

# REST Framework
router = routers.DefaultRouter()
router.register(r'api/users', views.UserViewSet)
router.register(r'api/groups', views.GroupViewSet)

urlpatterns = patterns(
    '',

    # Importamos las URLS del resto de apps:
    url(r'^', include('landing.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^profile/(?P<username>[\w-]+)/$', 'user_profile.views.profile_view', name='profile'),
    url(r'^search/$','user_profile.views.search'),
    url(r'^config/changepass/$', 'user_profile.views.config_changepass'),
    url(r'^config/profile/$', 'user_profile.views.config_profile'),
    #url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    url(r'^like_profile/$', 'user_profile.views.like_profile', name='like_profile'),
    url(r'^friends/$', 'user_profile.views.friends'),
    url(r'^respond_friend_request/$', 'user_profile.views.respond_friend_request', name='respond_friend_request'),
    url(r'^load_friends/$', 'user_profile.views.load_friends'),
    url(r'^config/privacity/$','user_profile.views.config_privacity'),
    url(r'^request_friend/$', 'user_profile.views.request_friend'),
    url(r'^publication/$', 'publications.views.publication_form'),
    url(r'^load_publications/$', 'publications.views.load_publications'),
    url(r'^load_publications/$', 'publications.views.load_publications'),
    url(r'^accounts/password/change/confirmation', 'user_profile.views.changepass_confirmation'),
    url(r'^accounts/password/change', user_profile_views.custom_password_change),
    url(r'^accounts/', include('allauth.urls')),
    # url django-photologe(galeria de fotos) 
    # url(r'^photologue/', include('photologue.urls', namespace='photologue')),
    # url novedades e inicio
    url(r'^inicio/$','user_profile.views.news_and_updates'),
    # url mensajes privados
    url(r'^messages/', include('django_messages.urls')),
    # About skyfolk
    url(r'^about/([^/]+)/$',about),
    # Market Skyfolk
    url(r'^market/$',market_inicio),
    # Relaciones usuario
    url(r'^relations/(?P<username>[\w-]+)/$',relaciones_user),
    # Importamos las urls de REST Framework
    url(r'^', include(router.urls)),
    url(
        r'^api-auth/',
        include(
            'rest_framework.urls',
            namespace='rest_framework'
        )
    ),
    url(r'^emoji/', include('emoji.urls')),
)
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
