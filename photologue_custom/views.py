from user_profile.models import PhotoExtended
from photologue.views import PhotoListView, PhotoDetailView
from publications.forms import PublicationForm
from user_profile.forms import SearchForm
from django.contrib.auth.decorators import login_required
from utils.ajaxable_reponse_mixin import AjaxableResponseMixin
from django.views.generic.edit import CreateView
from django.db import IntegrityError
from .forms import UploadNewPhoto, UploadNewPhotoExtended
from photologue.models import Photo
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from django.forms.formsets import formset_factory


class PhotoList(PhotoListView):
    template_name = "account/photo_gallery.html"
    paginate_by = 20
    queryset = None
    publicationForm = PublicationForm()
    searchForm = SearchForm()
    uploadFormExtended = UploadNewPhotoExtended(prefix='form2')

    def get_queryset(self):
        self.username = self.kwargs['username'][:-1]
        queryset = PhotoExtended.objects.filter(owner__username=self.username)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(PhotoList, self).get_context_data(**kwargs)
        context['publicationForm'] = self.publicationForm
        context['searchForm'] = self.searchForm
        context['object_list'] = self.get_queryset()
        context['user_gallery'] = self.username
        context['uploadFormExtended'] = self.uploadFormExtended

        return context

user_gallery = login_required(PhotoList.as_view())

class PhotoDetail(PhotoDetailView):
    template_name = "account/photo_detail.html"

photo_detail = login_required(PhotoDetail.as_view())
