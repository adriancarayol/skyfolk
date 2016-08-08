from django.conf.urls import url

urlpatterns = [
    # url add to timeline
    url(r'^timeline/add_to_timeline/$', 'timeline.views.add_to_timeline', name='add_to_timeline'),
    # url remove timeline
    url(r'^timeline/remove_timeline/$', 'timeline.views.remove_timeline', name='remove_timeline'),
]
