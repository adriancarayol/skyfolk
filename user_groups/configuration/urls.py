from django.conf.urls import url
from user_groups.configuration import views as configuration_views

urlpatterns = [
    url(r'^config/(?P<pk>\d+)/$', configuration_views.ConfigurationGroupProfile.as_view(),
        name='configuration_group'),
]