from django.conf.urls import patterns, url
from landing import views
from allauth.account import views as allauth_views

urlpatterns = patterns(
    '',
    #url(r'^$', views.landing, name='landing'),
    url(r'^$', allauth_views.login)
)
