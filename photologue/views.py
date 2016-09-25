import warnings

from django.views.generic.dates import ArchiveIndexView, DateDetailView, DayArchiveView, MonthArchiveView, \
    YearArchiveView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.base import RedirectView

from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404

from .models import Photo, Gallery
from publications.forms import PublicationForm
from user_profile.forms import SearchForm

from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from .forms import UploadFormPhoto, EditFormPhoto, UploadZipForm
from django.http import QueryDict, HttpResponse
import json
from django.shortcuts import redirect


# Gallery views.


class GalleryListView(ListView):
    queryset = Gallery.objects.on_site().is_public()
    paginate_by = 20


class GalleryDetailView(DetailView):
    queryset = Gallery.objects.on_site().is_public()


class GalleryDateView(object):
    queryset = Gallery.objects.on_site().is_public()
    date_field = 'date_added'
    allow_empty = True


class GalleryDateDetailView(GalleryDateView, DateDetailView):
    pass


class GalleryArchiveIndexView(GalleryDateView, ArchiveIndexView):
    pass


class GalleryDayArchiveView(GalleryDateView, DayArchiveView):
    pass


class GalleryMonthArchiveView(GalleryDateView, MonthArchiveView):
    pass


class GalleryYearArchiveView(GalleryDateView, YearArchiveView):
    make_object_list = True

# Collection views
@login_required(login_url='accounts/login')
def collection_list(request, username, photo_id):
    """
    Busca fotografias con tags muy parecidos o iguales
    :return => Devuelve una lista de fotos con un parecido:
    """
    user = request.user
    publicationForm = PublicationForm()
    searchForm = SearchForm()
    form = UploadFormPhoto()
    form_zip = UploadZipForm(request.POST, request.FILES, request=request)

    if request.method == 'POST':
        photo = Photo.objects.get(id=photo_id, owner__username=username)
        object_list = photo.tags.similar_objects()
        return render(request, 'photologue/photo_gallery.html', {'publicationForm': publicationForm,
                                                                    'searchForm': searchForm,
                                                                    'object_list': object_list, 'form': form,
                                                                    'form_zip': form_zip})
    else:
        return render(request, 'photologue/photo_gallery.html', {'publicationForm': publicationForm,
                                                                    'searchForm': searchForm, 'form': form,
                                                                    'form_zip': form_zip})


# Photo views.
@login_required(login_url='accounts/login')
def photo_list(request, username):
    """
    Vista para mostrar las imágenes del usuario
    """
    publicationForm = PublicationForm()
    searchForm = SearchForm()


    user_profile = get_object_or_404(get_user_model(),
                                     username__iexact=username)

    object_list = Photo.objects.filter(owner__username=username)

    form = UploadFormPhoto()
    form_zip = UploadZipForm(request.POST, request.FILES, request=request)

    return render(request, 'photologue/photo_gallery.html', {'form': form, 'object_list': object_list,
                                                             'user_gallery': username,
                                                             'publicationForm': publicationForm,
                                                             'searchForm': searchForm, 'form_zip': form_zip})


def upload_photo(request):
    """
    Función para subir una nueva foto a la galeria del usuario
    """
    user = request.user

    if request.method == 'POST':
        import pprint  # Para imprimir el file y los datos del form
        pprint.pprint(request.POST)
        pprint.pprint(request.FILES)
        form = UploadFormPhoto(data=request.POST, files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = user
            obj.save()
            form.save_m2m()  # Para guardar los tags de la foto
            return redirect('/media/'+user.username+'/')
        else:
            print(form.errors)
    else:
        return HttpResponse(
            json.dumps({"nothing to see": "this isn't happening"}),
            content_type="application/json"
        )


def upload_zip_form(request):
    """
    Función para subir un .zip a la galeria de un usuario
    """
    user = request.user
    if request.method == 'POST':
        form = UploadZipForm(data=request.POST, files=request.FILES, request=request)
        if form.is_valid():
            form.save(request=request)
            return redirect('/media/' + user.username + '/')
        else:
            return HttpResponse(
                json.dumps({"nothing to see": "this isn't happening"}),
                content_type="application/json"
            )
    else:
        return HttpResponse(
            json.dumps({"nothing to see": "no post method"}),
            content_type="application/json"
        )

@login_required()
def delete_photo(request):
    """
    Eliminamos una foto, comprobamos si el solicitante
    es el autor de la foto, si es asi, procedemos.
    """
    if request.method == 'DELETE':
        _id = int(QueryDict(request.body).get('id'))
        photo_to_delete = get_object_or_404(Photo, id=_id)

        if request.user.pk == photo_to_delete.owner_id:
            photo_to_delete.delete()
            response_data = {}
            response_data['msg'] = 'Photo was deleted.'
            response_data['author'] = request.user.username

            return HttpResponse(
                json.dumps(response_data),
                content_type="application/json"
            )
        else:
            return HttpResponse(
                json.dumps({"nothing to see": "this isn't happening"}),
                content_type="application/json"
            )
    else:
        return HttpResponse(
            json.dumps({"nothing to see": "this isn't happening"}),
            content_type="application/json"
        )


@login_required()
def edit_photo(request, photo_id):
    """
    Permite al creador de la imagen
    editar los atributos title, caption y tags.
    """
    photo = get_object_or_404(Photo, id=photo_id)
    form = EditFormPhoto(request.POST or None, instance=photo)
    if form.is_valid():
        if photo.owner.pk == request.user.pk:
            response_data = {'msg': 'Photo was edited!'}
            form.save()
        else:
            response_data = {'msg': 'You cant edit this photo.'}
        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )
    else:
        return HttpResponse(
            json.dumps({'Nothing to see': 'This isnt happening'}),
            content_type='application/json'
        )


class PhotoDetailView(DetailView):
    """
    Modificado por @adriancarayol.
    Cogemos el parametro de la url (para mostrar los detalles de la foto)
    """
    template_name = 'photologue/photo_detail.html'
    model = Photo

    def get_queryset(self):
        slug = self.kwargs['slug']
        return Photo.objects.filter(slug=slug)

    def get_context_data(self, **kwargs):
        context = super(PhotoDetailView, self).get_context_data(**kwargs)
        context['form'] = EditFormPhoto(instance=self.object)
        context['publicationForm'] = PublicationForm()
        context['searchForm'] = SearchForm()
        # Obtenemos la siguiente imagen y comprobamos si pertenece a nuestra propiedad
        try:
            next = self.object.get_next_by_date_added()
            context['next'] = next if next.owner == self.request.user else None
        except Photo.DoesNotExist:
            pass
        # Obtenemos la anterior imagen y comprobamos si pertenece a nuestra propiedad
        try:
            previous = self.object.get_previous_by_date_added()
            context['previous'] = previous if previous.owner == self.request.user else None
        except Photo.DoesNotExist:
            pass
        return context


class PhotoDateView(object):
    queryset = Photo.objects.on_site().is_public()
    date_field = 'date_added'
    allow_empty = True


class PhotoDateDetailView(PhotoDateView, DateDetailView):
    pass


class PhotoArchiveIndexView(PhotoDateView, ArchiveIndexView):
    pass


class PhotoDayArchiveView(PhotoDateView, DayArchiveView):
    pass


class PhotoMonthArchiveView(PhotoDateView, MonthArchiveView):
    pass


class PhotoYearArchiveView(PhotoDateView, YearArchiveView):
    make_object_list = True


# Deprecated views.

class DeprecatedMonthMixin(object):
    """Representation of months in urls has changed from a alpha representation ('jan' for January)
    to a numeric representation ('01' for January).
    Properly deprecate the previous urls."""

    query_string = True

    month_names = {'jan': '01',
                   'feb': '02',
                   'mar': '03',
                   'apr': '04',
                   'may': '05',
                   'jun': '06',
                   'jul': '07',
                   'aug': '08',
                   'sep': '09',
                   'oct': '10',
                   'nov': '11',
                   'dec': '12', }

    def get_redirect_url(self, *args, **kwargs):
        print('a')
        warnings.warn(
            DeprecationWarning('Months are now represented in urls by numbers rather than by '
                               'their first 3 letters. The old style will be removed in Photologue 3.4.'))


class GalleryDateDetailOldView(DeprecatedMonthMixin, RedirectView):
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        super(GalleryDateDetailOldView, self).get_redirect_url(*args, **kwargs)
        return reverse('photologue:gallery-detail', kwargs={'year': kwargs['year'],
                                                            'month': self.month_names[kwargs['month']],
                                                            'day': kwargs['day'],
                                                            'slug': kwargs['slug']})


class GalleryDayArchiveOldView(DeprecatedMonthMixin, RedirectView):
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        super(GalleryDayArchiveOldView, self).get_redirect_url(*args, **kwargs)
        return reverse('photologue:gallery-archive-day', kwargs={'year': kwargs['year'],
                                                                 'month': self.month_names[kwargs['month']],
                                                                 'day': kwargs['day']})


class GalleryMonthArchiveOldView(DeprecatedMonthMixin, RedirectView):
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        super(GalleryMonthArchiveOldView, self).get_redirect_url(*args, **kwargs)
        return reverse('photologue:gallery-archive-month', kwargs={'year': kwargs['year'],
                                                                   'month': self.month_names[kwargs['month']]})


class PhotoDateDetailOldView(DeprecatedMonthMixin, RedirectView):
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        super(PhotoDateDetailOldView, self).get_redirect_url(*args, **kwargs)
        return reverse('photologue:photo-detail', kwargs={'year': kwargs['year'],
                                                          'month': self.month_names[kwargs['month']],
                                                          'day': kwargs['day'],
                                                          'slug': kwargs['slug']})


class PhotoDayArchiveOldView(DeprecatedMonthMixin, RedirectView):
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        super(PhotoDayArchiveOldView, self).get_redirect_url(*args, **kwargs)
        return reverse('photologue:photo-archive-day', kwargs={'year': kwargs['year'],
                                                               'month': self.month_names[kwargs['month']],
                                                               'day': kwargs['day']})


class PhotoMonthArchiveOldView(DeprecatedMonthMixin, RedirectView):
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        super(PhotoMonthArchiveOldView, self).get_redirect_url(*args, **kwargs)
        return reverse('photologue:photo-archive-month', kwargs={'year': kwargs['year'],
                                                                 'month': self.month_names[kwargs['month']]})
