from django.urls import path
from . import views

app_name = 'external_services_twitter'

urlpatterns = [
    path('twitter/oauth/', views.auth_twitter_view),
    path('twitter/callback/', views.create_twitter_service_view),
]