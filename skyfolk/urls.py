from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from principal.forms import AuthForm
from userena import views as userena_views
from principal.forms import AuthenticationForm
from rest_framework import viewsets, routers
from api import views

admin.autodiscover()

# REST Framework
router = routers.DefaultRouter()
router.register(r'api/users', views.UserViewSet)
router.register(r'api/groups', views.GroupViewSet)

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'skyfolk.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$','principal.views.inicio'),
    url(r'^newuser/$','principal.views.new_user'),
    url(r'^profile/(?P<username>[\w-]+)/$', 'principal.views.profile_view', name='profile'),
    url(r'^search/$','principal.views.search'),
    url(r'^friends/$','principal.views.friends'),
    url(r'^outsession/$', 'principal.views.out_session'),
    url(r'^configprofile/$', 'principal.views.config_profile', name='search'),
    url(r'^newsevent/$','principal.views.news_event'),
    # URLS USERENA
    url(r'^accounts/signin/$', userena_views.signin, {'auth_form': AuthenticationForm}, name='userena_signin'),
    url(r'^accounts/(?P<username>(?!signout|signup|signin)[\.\w-]+)/$', 'principal.views.myprofile_detail', name='userena_profile_detail'),
    url(r'^accounts/', include('userena.urls')),

    # URLS REST FRAMEWORK
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
)