from django.urls import path
from django.conf.urls import include
from . import views

app_name = 'external_services'

urlpatterns = [
    path('services/twitter/', include('external_services.twitter.urls', namespace='twitter-service')),
    path('services/instagram/', include('external_services.instagram.urls', namespace='instagram-service')),
    path('all/', views.list_service_view, name='all-external-services'),
    path('services/delete/<int:pk>/', views.delete_user_service_view, name='delete-user-service')
]