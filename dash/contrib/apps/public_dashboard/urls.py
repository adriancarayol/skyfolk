from django.conf.urls import url

from dash.contrib.apps.public_dashboard import views as public_dashboard_views

urlpatterns = [
               # View public dashboard workspace.
               url(r'^(?P<username>[\w_\-]+)/(?P<workspace>[\w_\-]+)/$', public_dashboard_views.public_dashboard,
                   name='dash.public_dashboard'),

               # View public dashboard (no workspace selected == default workspace used).
               url(r'^(?P<username>[\w_\-]+)/$', public_dashboard_views.public_dashboard, name='dash.public_dashboard'),
               ]
