from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from principal.forms import AuthForm

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'skyfolk.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$','principal.views.inicio'),
    #url(r'^$','principal.views.inicio','django.contrib.auth.views.login',{'template_name': 'inicio.html','authentication_form': AuthForm}),
    url(r'^newuser/$','principal.views.new_user'),
    #url(r'^profile/', 'principal.views.profile'),
    #url(r'^profile/(?P<id>\d+)/$', 'principal.views.profile_view', name='profile'),
    url(r'^profile/(?P<username>[\w-]+)/$', 'principal.views.profile_view', name='profile'),
    url(r'^outsession/$', 'principal.views.out_session'),
)
