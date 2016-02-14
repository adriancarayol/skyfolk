from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns, static
from rest_framework import routers, viewsets, routers

from about.views import about
from api import views
from market.views import market_inicio
from relaciones.views import relaciones_user
from user_profile import views as user_profile_views
from user_profile.views import welcomeView, welcomeStep1
import notifications

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
    url(r'^setfirstLogin/', 'user_profile.views.setfirstLogin', name='setfirstLogin'),
    url(r'^profile/(?P<username>[\w-]+)/$', 'user_profile.views.profile_view', name='profile'),
    url(r'^search/$','user_profile.views.search'),
    url(r'^config/changepass/$', 'user_profile.views.config_changepass'),
    url(r'^config/profile/$', 'user_profile.views.config_profile'),
    #url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    url(r'^like_profile/$', 'user_profile.views.like_profile', name='like_profile'),
    url(r'^friends/(?P<username>[\w-]+)/$', 'user_profile.views.friends'),
    url(r'^respond_friend_request/$', 'user_profile.views.respond_friend_request', name='respond_friend_request'),
    url(r'^load_friends/$', 'user_profile.views.load_friends'),
    url(r'^config/privacity/$','user_profile.views.config_privacity'),
    url(r'^request_friend/$', 'user_profile.views.request_friend'),
    url(r'^add_friend_by_pin/$', 'user_profile.views.add_friend_by_username_or_pin'),
    url(r'^publication/$', 'publications.views.publication_form'),
    url(r'^publication/delete/$', 'publications.views.delete_publication', name='delete_publication'),
    url(r'^publication/add_like/$', 'publications.views.add_like', name='add_like'),
    url(r'^load_publications/$', 'publications.views.load_publications'),
    #url(r'^load_publications/$', 'publications.views.load_publications'),
    url(r'^accounts/password/change/confirmation', 'user_profile.views.changepass_confirmation'),
    url(r'^accounts/password/change', user_profile_views.custom_password_change),
    url(r'^accounts/', include('allauth.urls')),
    # url django-photologe(galeria de fotos)
    # url(r'^photologue/', include('photologue.urls', namespace='photologue')),
    # url add to timeline
    url(r'^timeline/addToTimeline/$', 'timeline.views.addToTimeline', name='add_timeline'),
    url(r'^timeline/removeTimeline/$', 'timeline.views.removeTimeline', name='remove_timeline'),
    # url novedades e inicio
    url(r'^inicio/mypublications/','latest_news.views.news_and_updates'),
    # url mensajes privados
    url(r'^messages/', include('django_messages.urls'), name="inbox"),
    # About skyfolk
    url(r'^about/([^/]+)/$',about),
    # Market Skyfolk
    url(r'^market/$',market_inicio),
    # Menciones en comentarios
    url(r'^get_mentions/', 'publications.views.get_mentions', name='get_mentions'),
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
    url(r'^emoji/', include('emoji.urls', namespace="emoji")),
    # Página de bienvenida a nuevos usuarios.
    url(r'^welcome/(?P<username>[\w-]+)/$', 'user_profile.views.welcomeView'),
    # Página de bienvenida, paso 1.
    url(r'^step1/(?P<username>[\w-]+)/$', welcomeStep1.as_view()),
    #notificaciones
    url('^(?P<username>[\w-]+)/notifications/', include('notifications.urls', namespace='notifications')),
)

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
