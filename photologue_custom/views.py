from user_profile.models import PhotoExtended
from photologue.views import PhotoListView, PhotoDetailView
from publications.forms import PublicationForm
from user_profile.forms import SearchForm
from django.contrib.auth.decorators import login_required
from utils.ajaxable_reponse_mixin import AjaxableResponseMixin
from django.views.generic.edit import CreateView
from django.db import IntegrityError
from .forms import UploadNewPhoto, UploadNewPhotoExtended, UploadNewPhotoFormSet
from photologue.models import Photo
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

class PhotoList(PhotoListView):
    template_name = "account/photo_gallery.html"
    paginate_by = 20
    queryset = None
    publicationForm = PublicationForm()
    searchForm = SearchForm()
    uploadForm = UploadNewPhoto()
    uploadSetForm = UploadNewPhotoFormSet()

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
        context['uploadForm'] = self.uploadForm
        context['uploadSetForm'] = self.uploadSetForm

        return context

user_gallery = login_required(PhotoList.as_view())

class PhotoDetail(PhotoDetailView):
    template_name = "account/photo_detail.html"

photo_detail = login_required(PhotoDetail.as_view())

class UploadNewPhotoView(AjaxableResponseMixin, CreateView):
    model = Photo
    form_class = UploadNewPhoto
    success_url = '/thanks/'

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        upload_set_form = UploadNewPhotoFormSet(self.request.POST, prefix='form_set')
        if (form.is_valid() and upload_set_form.is_valid()):
            return self.form_valid(form) and self.form_valid(upload_set_form)
        else:
            return self.form_invalid(form) and self.form_invalid(upload_set_form)

upload_new_photo = login_required(UploadNewPhotoView.as_view())