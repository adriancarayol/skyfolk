from django.conf.urls import include, url

urlpatterns = [url(r"^profile/", include("api.user_profile_api.urls"))]
