from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns, static
from django.views.generic import TemplateView

# from rest_framework import routers

# from api import views

admin.autodiscover()

# REST Framework
# router = routers.DefaultRouter()
# router.register(r'api/users', views.UserViewSet)
# router.register(r'api/groups', views.GroupViewSet)

urlpatterns = [
    # Importamos las URLS del resto de apps:
    url(r'^', include('landing.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('allauth.urls')),  # django-allauth
    # urls support
    url(r'^', include('support.urls', namespace="support"), name="support"),
    # urls user_profile
    url(r'^', include('user_profile.urls', namespace="user_profile"), name="user_profile"),
    # urls para grupos de usuarios
    url(r'^', include('user_groups.urls', namespace="user_groups"), name="user_groups"),
    # url(r'^config/changepass/$', 'user_profile.views.config_changepass'),
    # url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
    # {'document_root': settings.MEDIA_ROOT}),
    # url publications
    url(r'^', include('publications.urls', namespace="publications"), name="publications"),
    url(r'^', include('publications_groups.urls', namespace="publications_groups"),
        name="publications_groups"),
    # Publicaciones en imagenes de la galeria
    url(r'^', include('publications_gallery.urls', namespace="publications_gallery"), name="publications_gallery"),
    # url novedades e inicio
    url(r'^', include('latest_news.urls', namespace="latest_news"), name="news"),
    # url mensajes privados

    # About skyfolk
    url(r'^', include('about.urls')),
    # Recomendacion password para usuarios
    url(r'^tips/password/$', TemplateView.as_view(
        template_name='about/password_recommendation.html')),
    # Importamos las urls de REST Framework
    # url(r'^', include(router.urls)),
    # url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # Urls para el modulo emoji
    url(r'^emoji/', include('emoji.urls', namespace="emoji")),
    # Django-avatar
    url(r'^', include('avatar.urls')),
    # notificaciones
    # url('^(?P<username>[\w-]+)/notifications/', include('notifications.urls',
    # namespace='notifications')),
    url('^inbox/notifications/', include('notifications.urls',
                                         namespace='notifications')),
    # django-photologue
    url(r'^', include('photologue.urls', namespace='photologue')),  # original photologue
    url(r'^group/', include('photologue_groups.urls', namespace='photologue_groups')),  # photologue groups
    url(r'^messages/', include('postman.urls', namespace='postman', app_name='postman')),
    # django-dash URLs:
    # url(r'^dashboard/', include('dash.urls')),
    # url(r'^dash/contrib/plugins/rss-feed/', include('dash.contrib.plugins.rss_feed.urls')),
    # url(r'^contrib/', include('dash.contrib.apps.public_dashboard.urls')),
    # feedback
    url(r'^tellme/', include("tellme.urls")),
    # logros
    url(r'^badges/', include('badgify.urls')),
    url(r'^awards/', include('awards.urls')),
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
                      url(r'^__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns
