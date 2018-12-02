from django.urls import path
from . import views

app_name = 'external_services_youtube'

urlpatterns = [
    path('oauth/', views.auth_youtube_view, name='connect-youtube-service'),
    path('callback/', views.create_youtube_service_view, name='callback-youtube-service'),
]