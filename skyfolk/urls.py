#encoding:utf-8
from django.conf.urls import patterns, include, url
from django.contrib import admin
#from rest_framework import viewsets, routers
from rest_framework import routers
from api import views
from django.conf import settings


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
    url(r'^request_friend/$', 'user_profile.views.request_friend'),
    url(r'^publication/$', 'publications.views.publication_form'),
    url(r'^load_publications/$', 'publications.views.load_publications'),
    url(r'^accounts/', include('allauth.urls')),

    # url mensajes privados
    url(r'^messages/', include('django_messages.urls')),

    # Importamos las urls de REST Framework
    url(r'^', include(router.urls)),
    url(
        r'^api-auth/',
        include(
            'rest_framework.urls',
            namespace='rest_framework'
        )
    )
)
