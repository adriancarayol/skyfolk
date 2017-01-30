from django.conf.urls import url
from cropper import views as cropper_views

urlpatterns = [
	url(r'^crop/$', cropper_views.cropper_js,
        name='crop-image'),
]