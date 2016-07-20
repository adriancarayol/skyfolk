from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns, static
from rest_framework import routers, viewsets, routers

from about.views import about
from api import views
#from market.views import market_inicio
#from relaciones.views import relaciones_user
from user_profile import views as user_profile_views
#from user_profile.views import welcomeView, welcomeStep1
import notifications
# import notifications
from publications.views import PublicationNewView, PublicationsListView
from django.views.generic import TemplateView

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
    # CUSTOM URL EMAIL CONFIG
    url(r"^config/email/$", 'allauth.account.views.email', name="account_email"),
    url(r'^search/$','user_profile.views.search'),
    #url(r'^config/changepass/$', 'user_profile.views.config_changepass'),
    url(r'^config/profile/$', 'user_profile.views.config_profile'), # URL CONFIG PROFILE USER
    url(r'^config/privacity/$', 'user_profile.views.config_privacity'), # URL CHANGE PRIVACITY
    url(r'^config/pincode/$', 'user_profile.views.config_pincode'),  # CONSULTAR PINCODE
    #url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    url(r'^like_profile/$', 'user_profile.views.like_profile', name='like_profile'),
    url(r'^following/(?P<username>[\w-]+)/$', 'user_profile.views.following'),
    url(r'^followers/(?P<username>[\w-]+)/$', 'user_profile.views.followers'),
    url(r'^respond_friend_request/$', 'user_profile.views.respond_friend_request', name='respond_friend_request'),
    url(r'^load_followers/$', 'user_profile.views.load_followers'), # Cargar mas followers
    url(r'^load_follows/$', 'user_profile.views.load_follows'), # Cargar mas follows
    url(r'^request_friend/$', 'user_profile.views.request_friend'),
    url(r'^remove_relationship/$', 'user_profile.views.remove_relationship'),
    url(r'^remove_request_follow/$', 'user_profile.views.remove_request_follow'),
    url(r'^add_friend_by_pin/$', 'user_profile.views.add_friend_by_username_or_pin'),
    # url(r'^publication/$', 'publications.views.publication_form'),
    url(r'^publication/$', PublicationNewView.as_view(), name='new_publication'),
    url(r'^publication/delete/$', 'publications.views.delete_publication', name='delete_publication'),
    url(r'^publication/list/$', PublicationsListView.as_view(), name='last_publication'),
    url(r'^publication/add_like/$', 'publications.views.add_like', name='add_like'),
    url(r'^publication/add_hate/$', 'publications.views.add_hate', name='add_hate'),
    url(r'^load_publications/$', 'publications.views.load_publications'),
    #url(r'^load_publications/$', 'publications.views.load_publications'),
    url(r'^accounts/password/change/confirmation', 'user_profile.views.changepass_confirmation'),
    url(r'^config/password/change/$', user_profile_views.custom_password_change), # URL CHANGE PASSWORD
    url(r'^accounts/', include('allauth.urls')),
    # url django-photologe(galeria de fotos)
    # url(r'^photologue/', include('photologue.urls', namespace='photologue')),
    # url add to timeline
    url(r'^timeline/addToTimeline/$', 'timeline.views.addToTimeline', name='add_timeline'),
    # url remove timeline
    url(r'^timeline/removeTimeline/$', 'timeline.views.removeTimeline', name='remove_timeline'),
    # url novedades e inicio
    url(r'^inicio/mypublications/','latest_news.views.news_and_updates'),
    # url mensajes privados
    url(r'^messages/', include('django_messages.urls'), name="inbox"),
    # About skyfolk
    url(r'^about/([^/]+)/$', about),
    # Recomendacion password para usuarios
    url(r'^tips/password/$', TemplateView.as_view(template_name='about/password_recommendation.html')),
    # Importamos las urls de REST Framework
    url(r'^', include(router.urls)),
    url(
        r'^api-auth/',
        include(
            'rest_framework.urls',
            namespace='rest_framework'
        )
    ),
    # Urls para el modulo emoji
    url(r'^emoji/', include('emoji.urls', namespace="emoji")),
    # Django-avatar
    (r'^/', include('avatar.urls')),
    # Página de bienvenida a nuevos usuarios.
    url(r'^welcome/(?P<username>[\w-]+)/$', 'user_profile.views.welcomeView'),
    # Página de bienvenida, paso 1.
    url(r'^step1/(?P<username>[\w-]+)/$', 'user_profile.views.welcomeStep1', name='welcomeStep1'),
    #notificaciones
    #url('^(?P<username>[\w-]+)/notifications/', include('notifications.urls', namespace='notifications')),
    url('^inbox/notifications/', include('notifications.urls', namespace='notifications')),
)

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
