from django.urls import path
from . import views

app_name = "external_services_twitter"

urlpatterns = [
    path("oauth/", views.auth_twitter_view, name="connect-twitter-service"),
    path(
        "callback/", views.create_twitter_service_view, name="callback-twitter-service"
    ),
]
