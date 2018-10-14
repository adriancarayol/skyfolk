from django.urls import path
from django.conf.urls import include
from . import views

app_name = 'external_services'

urlpatterns = [
    path('services/', include('external_services.twitter.urls')),
    path('all/', views.list_service_view, name='all-external-services')
]