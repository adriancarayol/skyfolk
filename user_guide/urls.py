from django.conf.urls import url

from user_guide import views

app_name = 'user_guide'

urlpatterns = [
    url(r'^seen/?$', views.GuideSeenView.as_view(), name='user_guide.seen')
]
