from django.conf.urls import url

from user_groups.configuration import views as configuration_views

app_name = 'user_groups_configuration'

urlpatterns = [
    url(r'^config/(?P<pk>\d+)/$', configuration_views.ConfigurationGroupProfile.as_view(),
        name='configuration_group'),
    url(r'^config/delete/(?P<pk>\d+)/$', configuration_views.DeleteGroup.as_view(),
        name='configuration_delete_group'),

]