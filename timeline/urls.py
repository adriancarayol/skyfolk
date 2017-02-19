from django.conf.urls import url

from timeline import views as timeline_views

urlpatterns = [
    # url add to timeline
    url(r'^timeline/add_to_timeline/$', timeline_views.add_to_timeline,
        name='add_to_timeline'),
    # url remove timeline
    url(r'^timeline/remove_timeline/$', timeline_views.remove_timeline,
        name='remove_timeline'),
]
