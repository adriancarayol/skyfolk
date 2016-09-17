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
# from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model

from .forms import UploadFormPhoto
from django.http import QueryDict, HttpResponse
import json


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


# Photo views.
@login_required(login_url='accounts/login')
def photo_list(request, username):
    """
    Vista para mostrar las imágenes del usuario
    """
    publicationForm = PublicationForm()
    searchForm = SearchForm()

    user = request.user

    user_profile = get_object_or_404(get_user_model(),
                                     username__iexact=username)

    object_list = Photo.objects.filter(owner__username=username)

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
        else:
            print(form.errors)
    else:
        form = UploadFormPhoto()

    return render(request, 'photologue/photo_gallery.html', {'form': form, 'object_list': object_list,
                                                             'user_gallery': username,
                                                             'publicationForm': publicationForm,
                                                             'searchForm': searchForm})


@login_required()
def delete_photo(request):
    """
    Eliminamos una foto, comprobamos si el solicitante
    es el autor de la foto, si es asi, procedemos.
    """
    if request.method == 'DELETE':
        _id = int(QueryDict(request.body).get('postpk'))
        photo_to_delete = get_object_or_404(Photo, id=_id)

        if request.user.pk == photo_to_delete.owner_id:
            photo_to_delete.delete()
            response_data = {}
            response_data['msg'] = 'Photo was deleted.'

            return HttpResponse(
                json.dumps(response_data),
                content_type="application/json"
            )
        else:
            return HttpResponse(
                json.dumps({"nothing to see": "this isn't happening"}),
                content_type="application/json"
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
