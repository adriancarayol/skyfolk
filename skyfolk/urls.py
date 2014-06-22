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
    url(r'^like_profile/$', 'landing.views.like_profile', name='like_profile'),
    url(r'^accounts/', include('allauth.urls')),

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