from django.conf.urls import *
from photologue.views import GalleryListView
from django.views.generic.edit import CreateView
from photologue.models import Photo
urlpatterns = patterns(
    '',
    url(r'^gallerylist/$',GalleryListView.as_view(paginate_by=5), name='photologue_custom-gallery-list'),
    url(r'^media/(?P<username>[\w-]+/$)', 'photologue_custom.views.user_gallery', name='photo-list'),
    url(r'^photo/(?P<slug>[\-\d\w]+)/$', 'photologue_custom.views.photo_detail', name='pl-photo'),
    #url(r'^upload_new_photo/$', 'photologue_custom.views.upload_photo_view', name='new-photo'),
)