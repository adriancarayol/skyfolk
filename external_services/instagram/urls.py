from django.urls import path
from . import views

app_name = "external_services_twitter"

urlpatterns = [
    path("oauth/", views.auth_instagram_view, name="connect-instagram-service"),
    path(
        "callback/",
        views.create_instagram_service_view,
        name="callback-instagram-service",
    ),
]
