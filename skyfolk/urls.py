from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns, static
from rest_framework import routers, viewsets, routers

from about.views import about
from api import views
# from market.views import market_inicio
# from relaciones.views import relaciones_user
from user_profile import views as user_profile_views
# from user_profile.views import welcomeView, welcomeStep1
import notifications
# import notifications
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
    url(r'^accounts/', include('allauth.urls')),  # django-allauth
    # urls user_profile
    url(r'^', include('user_profile.urls'), name="user_profile"),
    # url(r'^config/changepass/$', 'user_profile.views.config_changepass'),
    # url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
    # {'document_root': settings.MEDIA_ROOT}),
    # url publications
    url(r'^', include('publications.urls'), name="publications"),
    # url(r'^publication/$', 'publications.views.publication_form'),
    # url django-photologe(galeria de fotos)
    # url(r'^photologue/', include('photologue.urls', namespace='photologue')),
    # urls timeline
    url(r'^', include('timeline.urls'), name="timeline"),
    # url novedades e inicio
    url(r'^', include('latest_news.urls'), name="news"),
    # url mensajes privados
    url(r'^messages/', include('django_messages.urls'), name="inbox"),
    # About skyfolk
    url(r'^about/([^/]+)/$', about),
    # Recomendacion password para usuarios
    url(r'^tips/password/$', TemplateView.as_view(
        template_name='about/password_recommendation.html')),
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
    # notificaciones
    # url('^(?P<username>[\w-]+)/notifications/', include('notifications.urls',
    # namespace='notifications')),
    url('^inbox/notifications/', include('notifications.urls',
        namespace='notifications')),
)

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
