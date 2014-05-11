#encoding:utf-8
from django.conf.urls import patterns, include, url
from django.contrib import admin
#from rest_framework import viewsets, routers
from rest_framework import routers
from api import views


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
