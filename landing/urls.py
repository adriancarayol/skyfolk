from allauth.account import views as allauth_views
from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    #url(r'^$', views.landing, name='landing'),
    url(r'^$', allauth_views.login)
)
