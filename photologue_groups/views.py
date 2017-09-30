import json
import warnings

from PIL import Image
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.db.models import Count, Q, Case, When, Value, IntegerField, OuterRef, Subquery
from django.http import Http404, HttpResponseForbidden
from django.http import JsonResponse
from django.http import QueryDict, HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.utils.six import BytesIO
from django.views.generic.base import RedirectView
from django.views.generic.dates import ArchiveIndexView, DateDetailView, DayArchiveView, MonthArchiveView, \
    YearArchiveView
from django.views.generic.detail import DetailView
from el_pagination.decorators import page_template
from el_pagination.views import AjaxListView

from itertools import chain

from publications.models import Publication
from publications_gallery.forms import PublicationPhotoForm, PublicationPhotoEdit, PublicationVideoEdit, \
    PublicationVideoForm
from publications.forms import SharedPublicationForm
from publications_gallery.models import PublicationPhoto, PublicationVideo
from user_profile.node_models import NodeProfile
from utils.forms import get_form_errors
from .forms import UploadFormPhoto, EditFormPhoto, UploadZipForm, UploadFormVideo, EditFormVideo
from .models import PhotoGroup, VideoGroup
from user_groups.models import UserGroups


# Collection views
@login_required(login_url='accounts/login')
@page_template("photologue/photo_gallery_page.html")
def collection_list(request, slug,
                    tag_slug,
                    template='photologue/photo_gallery.html',
                    extra_context=None):
    """
    Busca fotografias con tags muy parecidos o iguales
    :return => Devuelve una lista de fotos con un parecido:
    """

    user = request.user

    # Para comprobar si tengo permisos para ver el contenido de la coleccion
    try:
        user_profile = NodeProfile.nodes.get(title=username)
        m = NodeProfile.nodes.get(user_id=user.id)
    except NodeProfile.DoesNotExist:
        raise Http404

    visibility = user_profile.is_visible(m)

    if visibility and visibility != 'all':
        return redirect('user_profile:profile', username=user_profile.title)

    form = UploadFormPhoto()
    form_zip = UploadZipForm(request.POST, request.FILES, request=request)

    print('>>>>>>> TAGNAME {}'.format(tag_slug))
    if user.username == username:
        photos = PhotoGroup.objects.filter(owner__username=username,
                                           tags__name__exact=tag_slug)
        videos = VideoGroup.objects.filter(owner__username=username, tags__slug=tag_slug)
    else:
        photos = PhotoGroup.objects.filter(owner__username=username,
                                           tags__name__exact=tag_slug, is_public=True)
        videos = VideoGroup.objects.filter(owner__username=username, tags__slug=tag_slug, is_public=True)

    items = list(
        sorted(
            chain(videos, photos),
            key=lambda objects: objects.date_added,
            reverse=True
        ))

    context = {'object_list': items, 'form': form,
               'form_zip': form_zip, }

    if extra_context is not None:
        context.update(extra_context)

    return render(request, template, context)


class PhotoListView(AjaxListView):
    context_object_name = "object_list"
    template_name = "photologue_groups/photo_gallery.html"
    page_template = "photologue_groups/photo_gallery_page.html"

    def __init__(self):
        self.object = None
        super(PhotoListView, self).__init__()

    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.pop('slug')

        try:
            self.object = UserGroups.objects.get(slug=slug)
        except UserGroups.DoesNotExist:
            raise Http404

        if self.user_pass_test():
            return super(PhotoListView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect('user_groups:group-profile', groupname=slug)

    def get_queryset(self):
        if self.request.user.id == self.object.owner_id:
            photos = PhotoGroup.objects.filter(group=self.object).select_related('owner',
                                                                                 'effect').prefetch_related(
                'tags')
            videos = VideoGroup.objects.filter(group=self.object).select_related('owner').prefetch_related(
                'tags')
        else:
            photos = PhotoGroup.objects.filter(group=self.object, is_public=True).select_related('owner',
                                                                                                 'effect').prefetch_related(
                'tags')
            videos = VideoGroup.objects.filter(group=self.object, is_public=True).select_related(
                'owner').prefetch_related(
                'tags')

        items = list(
            sorted(
                chain(videos, photos),
                key=lambda objects: objects.date_added,
                reverse=True
            ))

        return items

    def get_context_data(self, **kwargs):
        context = super(PhotoListView, self).get_context_data(**kwargs)
        context['form'] = UploadFormPhoto()
        context['form_video'] = UploadFormVideo()
        context['form_zip'] = UploadZipForm(self.request.POST, self.request.FILES, request=self.request)
        context['group_gallery'] = self.object
        return context

    def user_pass_test(self):
        """
        Comprueba si un usuario tiene permisos
        para ver la galeria solicitada.
        """
        user = self.request.user
        user_profile = NodeProfile.nodes.get(user_id=self.object.owner_id)
        m = NodeProfile.nodes.get(user_id=user.id)

        visibility = user_profile.is_visible(m)

        if visibility and visibility != 'all':
            return False
        return True


photo_list = login_required(PhotoListView.as_view())


def upload_photo(request):
    """
    Función para subir una nueva foto a la galeria del grupo
    """
    user = request.user

    if request.method == 'POST':
        form = UploadFormPhoto(request.POST, request.FILES or None)
        if form.is_valid():
            pk = form.cleaned_data['pk']

            try:
                group = UserGroups.objects.get(pk=pk)
            except UserGroups.DoesNotExist:
                raise Http404

            if user.id != group.owner_id and not user.groups.filter(pk=pk).exists():
                return HttpResponseForbidden("No tienes permiso para subir una imagen al grupo {}".format(group.name))

            obj = form.save(commit=False)
            obj.owner = user
            obj.group_id = pk

            if 'image' in request.FILES:
                crop_image(obj, request)

            obj.is_public = not form.cleaned_data['is_public']

            obj.save()
            form.save_m2m()  # Para guardar los tags de la foto
            data = {
                'result': True,
                'state': 200,
                'message': 'Success',
                'content': render_to_string(request=request, template_name='channels/new_photo_gallery.html',
                                            context={'photo': obj})
            }
        else:
            data = {
                'result': False,
                'state': 415,
                'message': get_form_errors(form),
            }
    else:
        data = {
            'result': False,
            'state': 405,
            'message': 'Método no permitido',
        }
    return JsonResponse(data)


def upload_video(request):
    """
    Función para subir un nuevo video a la galeria del usuario
    """
    user = request.user

    if request.method == 'POST':
        form = UploadFormVideo(request.POST, request.FILES or None)
        if form.is_valid():
            pk = form.cleaned_data['pk']

            try:
                group = UserGroups.objects.get(pk=pk)
            except UserGroups.DoesNotExist:
                raise Http404

            if user.id != group.owner_id and not user.groups.filter(pk=pk).exists():
                return HttpResponseForbidden("No tienes permiso para subir una imagen al grupo {}".format(group.name))

            obj = form.save(commit=False)
            obj.owner = user
            obj.group_id = pk
            obj.is_public = not form.cleaned_data['is_public']

            obj.save()
            form.save_m2m()  # Para guardar los tags de la foto

            data = {
                'result': True,
                'state': 200,
                'message': 'Success',
                'content': '/multimedia/' + user.username
            }
        else:
            data = {
                'result': False,
                'state': 415,
                'message': get_form_errors(form),
            }
    else:
        data = {
            'result': False,
            'state': 405,
            'message': 'Método GET no permitido.',
        }
    return JsonResponse(data)


def crop_image(obj, request):
    """
    Recortar imagen
    """
    image = request.FILES['image']
    img_data = dict(request.POST.items())
    x = None  # Coordinate x
    y = None  # Coordinate y
    w = None  # Width
    h = None  # Height
    rotate = None  # Rotate
    is_cutted = True
    for key, value in img_data.items():  # Recorremos las opciones de recorte
        if key == "avatar_cut" and value == 'false':  # Comprobamos si el usuario ha recortado la foto
            is_cutted = False
            break
        if key == "avatar_data":
            str_value = json.loads(value)
            x = str_value.get('x')
            y = str_value.get('y')
            w = str_value.get('width')
            h = str_value.get('height')
            rotate = str_value.get('rotate')
    if image._size > settings.BACK_IMAGE_DEFAULT_SIZE:
        raise ValueError("Backimage > 5MB!")

    im = Image.open(image)
    fill_color = (255, 255, 255, 0)
    if im.mode in ('RGBA', 'LA'):
        background = Image.new(im.mode[:-1], im.size, fill_color)
        background.paste(im, im.split()[-1])
        im = background

    if is_cutted:  # el usuario ha recortado la foto
        tempfile = im.rotate(-rotate, expand=True)
        tempfile = tempfile.crop((int(x), int(y), int(w + x), int(h + y)))
        tempfile_io = BytesIO()
        tempfile.save(tempfile_io, format='JPEG', optimize=True, quality=90)
        tempfile_io.seek(0)
        image_file = InMemoryUploadedFile(tempfile_io, None, 'rotate.jpeg', 'image/jpeg', tempfile_io.tell(), None)
    else:  # no la recorta, optimizamos la imagen
        im.thumbnail((1200, 630), Image.ANTIALIAS)
        tempfile_io = BytesIO()
        im.save(tempfile_io, format='JPEG', optimize=True, quality=90)
        tempfile_io.seek(0)
        image_file = InMemoryUploadedFile(tempfile_io, None, 'rotate.jpeg', 'image/jpeg', tempfile_io.tell(), None)

    obj.image = image_file


def upload_zip_form(request):
    """
    Funcion para subir un .zip a la galeria de un usuario
    """
    user = request.user
    if request.method == 'POST':
        form = UploadZipForm(data=request.POST, files=request.FILES, request=request)
        if form.is_valid():
            form.save(request=request)
            return redirect('/multimedia/' + user.username + '/')
        else:
            # Cambiar por JsonResponse
            return redirect('/multimedia/' + user.username + '/')
    else:
        # Cambiar por JsonResponse
        return redirect('/multimedia/' + user.username + '/')


@login_required()
def delete_photo(request):
    """
    Eliminamos una foto, comprobamos si el solicitante
    es el autor de la foto, si es asi, procedemos.
    """
    if request.method == 'DELETE':
        user = request.user
        _id = int(QueryDict(request.body).get('id'))
        photo_to_delete = get_object_or_404(PhotoGroup, id=_id)

        if user.pk == photo_to_delete.owner_id:
            photo_to_delete.delete()
            response_data = {}
            response_data['msg'] = '¡Imagen eliminada!.'
            response_data['author'] = user.username

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
    photo = get_object_or_404(PhotoGroup, id=photo_id)
    form = EditFormPhoto(request.POST or None, instance=photo)
    user = request.user
    if form.is_valid():
        if photo.owner.pk == user.pk:
            response_data = {'msg': 'Photo was edited!'}
            form.save()
        else:
            response_data = {'msg': 'You cant edit this photo.'}
            return HttpResponse(
                json.dumps(response_data),
                content_type="application/json"
            )
        return redirect('/multimedia/' + user.username + '/')
    else:
        return HttpResponse(
            json.dumps({'Nothing to see': 'This isnt happening'}),
            content_type='application/json'
        )


@login_required()
def edit_video(request, video_id):
    """
    Permite al creador de la imagen
    editar los atributos title, caption y tags.
    """
    photo = get_object_or_404(VideoGroup, id=video_id)
    form = EditFormVideo(request.POST or None, instance=photo)
    user = request.user
    if form.is_valid():
        if photo.owner.pk == user.pk:
            response_data = {'msg': '¡Video editado con éxito!'}
            form.save()
        else:
            response_data = {'msg': 'No puedes editar este vídeo.'}
            return HttpResponse(
                json.dumps(response_data),
                content_type="application/json"
            )
        return redirect('/multimedia/' + user.username + '/')
    else:
        return HttpResponse(
            json.dumps({'Nothing to see': 'This isnt happening'}),
            content_type='application/json')


class PhotoDetailView(DetailView):
    """
    Cogemos el parametro de la url (para mostrar los detalles de la foto)
    """
    template_name = 'photologue/photo_detail.html'
    model = PhotoGroup

    def __init__(self):
        self.username = None
        self.photo = None
        super(PhotoDetailView, self).__init__()

    def dispatch(self, request, *args, **kwargs):
        self.photo = self.get_object(PhotoGroup.objects.filter(slug=self.kwargs['slug']) \
                                     .select_related('owner', 'effect') \
                                     .prefetch_related('tags'))
        self.username = self.photo.owner.username

        if self.user_pass_test():
            return super(PhotoDetailView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect('user_profile:profile', username=self.username)

    def get_context_data(self, **kwargs):
        context = super(PhotoDetailView, self).get_context_data(**kwargs)
        user = self.request.user
        page = self.request.GET.get('page', 1)

        shared_publications = Publication.objects.filter(shared_photo_publication__id=OuterRef('pk'),
                                                         deleted=False).order_by().values(
            'shared_photo_publication__id')

        total_shared_publications = shared_publications.annotate(c=Count('*')).values('c')

        shared_for_me = shared_publications.annotate(have_shared=Count(Case(
            When(author_id=user.id, then=Value(1))
        ))).values('have_shared')

        paginator = Paginator(
            PublicationPhoto.objects.annotate(likes=Count('user_give_me_like'),
                                              hates=Count('user_give_me_hate'), have_like=Count(Case(
                    When(user_give_me_like=user, then=Value(1)),
                    output_field=IntegerField()
                )), have_hate=Count(Case(
                    When(user_give_me_hate=user, then=Value(1)),
                    output_field=IntegerField()
                ))).annotate(total_shared=Subquery(total_shared_publications, output_field=IntegerField())).annotate(
                have_shared=Subquery(shared_for_me, output_field=IntegerField())).filter(
                ~Q(p_author__profile__from_blocked__to_blocked=user.profile)
                & Q(board_photo_id=self.photo.id),
                Q(level__lte=0) & Q(deleted=False)) \
                .prefetch_related('publication_photo_extra_content', 'images', 'videos') \
                .select_related('p_author',
                                'board_photo', 'parent'), 10)

        try:
            publications = paginator.page(page)
        except PageNotAnInteger:
            publications = paginator.page(1)
        except EmptyPage:
            publications = paginator.page(paginator.num_pages)

        context['publications'] = publications

        if self.request.is_ajax():
            self.template_name = 'photologue/publications_entries.html'
            return context

        initial_photo = {'p_author': user.pk, 'board_photo': self.photo}

        context['form'] = EditFormPhoto(instance=self.photo)
        context['publication_photo'] = PublicationPhotoForm(initial=initial_photo)
        context['publication_shared'] = SharedPublicationForm()
        context['publication_edit'] = PublicationPhotoEdit()

        # Obtenemos la siguiente imagen y comprobamos si pertenece a nuestra propiedad
        if self.photo.is_public:
            try:
                next = self.photo.get_next_in_gallery()
                context['next'] = next
            except PhotoGroup.DoesNotExist:
                pass
            # Obtenemos la anterior imagen y comprobamos si pertenece a nuestra propiedad
            try:
                previous = self.photo.get_previous_in_gallery()
                context['previous'] = previous
            except PhotoGroup.DoesNotExist:
                pass
        elif not self.photo.is_public and self.photo.owner.id == user.id:
            try:
                next = self.photo.get_next_in_own_gallery()

                context['next'] = next
            except PhotoGroup.DoesNotExist:
                pass
            # Obtenemos la anterior imagen y comprobamos si pertenece a nuestra propiedad
            try:
                previous = self.photo.get_previous_in_own_gallery()
                context['previous'] = previous
            except PhotoGroup.DoesNotExist:
                pass
        return context

    def user_pass_test(self):
        """
        Comprueba si un usuario tiene permisos
        para ver la galeria solicitada.
        """
        user = self.request.user
        if not self.photo.is_public and user.id != self.photo.owner.id:
            return False
        elif user.id == self.photo.owner.id:
            return True

        try:
            user_profile = NodeProfile.nodes.get(title=self.username)
            n = NodeProfile.nodes.get(user_id=user.id)
        except NodeProfile.DoesNotExist:
            raise Http404

        visibility = user_profile.is_visible(n)

        if visibility and visibility != 'all':
            return False
        return True


# Video Views

class VideoDetailView(DetailView):
    """
    Cogemos el parametro de la url (para mostrar los detalles de la foto)
    """
    template_name = 'photologue/videos/video_detail.html'
    model = VideoGroup

    def __init__(self):
        self.username = None
        super(VideoDetailView, self).__init__()

    def get_object(self, queryset=None):
        return get_object_or_404(VideoGroup.objects.select_related('owner').prefetch_related('tags'),
                                 slug=self.kwargs['slug'])

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()

        self.username = self.object.owner.username

        if self.user_pass_test():
            return super(VideoDetailView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect('user_profile:profile', username=self.username)

    def get_context_data(self, **kwargs):
        context = super(VideoDetailView, self).get_context_data(**kwargs)
        user = self.request.user
        page = self.request.GET.get('page', 1)

        shared_publications = Publication.objects.filter(shared_video_publication__id=OuterRef('pk'),
                                                         deleted=False).order_by().values(
            'shared_photo_publication__id')

        total_shared_publications = shared_publications.annotate(c=Count('*')).values('c')

        shared_for_me = shared_publications.annotate(have_shared=Count(Case(
            When(author_id=user.id, then=Value(1))
        ))).values('have_shared')

        paginator = Paginator(
            PublicationVideo.objects.annotate(likes=Count('user_give_me_like'),
                                              hates=Count('user_give_me_hate'), have_like=Count(Case(
                    When(user_give_me_like=user, then=Value(1)),
                    output_field=IntegerField()
                )), have_hate=Count(Case(
                    When(user_give_me_hate=user, then=Value(1)),
                    output_field=IntegerField()
                ))).annotate(total_shared=Subquery(total_shared_publications, output_field=IntegerField())).annotate(
                have_shared=Subquery(shared_for_me, output_field=IntegerField())).filter(
                ~Q(author__profile__from_blocked__to_blocked=user.profile)
                & Q(board_video_id=self.object.id),
                Q(level__lte=0) & Q(deleted=False)) \
                .prefetch_related('publication_video_extra_content', 'images', 'videos') \
                .select_related('author',
                                'board_video', 'parent'), 10)

        try:
            publications = paginator.page(page)
        except PageNotAnInteger:
            publications = paginator.page(1)
        except EmptyPage:
            publications = paginator.page(paginator.num_pages)

        context['publications'] = publications

        if self.request.is_ajax():
            self.template_name = 'photologue/videos/publications_entries.html'
            return context

        initial_video = {'author': user.pk, 'board_video': self.object}
        context['form'] = EditFormVideo(instance=self.object)
        context['publication_video'] = PublicationVideoForm(initial=initial_video)
        context['publication_shared'] = SharedPublicationForm()
        context['publication_edit'] = PublicationVideoEdit()

        # Obtenemos la siguiente imagen y comprobamos si pertenece a nuestra propiedad
        if self.object.is_public:
            try:
                next = self.object.get_next_in_gallery()
                context['next'] = next
            except PhotoGroup.DoesNotExist:
                pass
            # Obtenemos la anterior imagen y comprobamos si pertenece a nuestra propiedad
            try:
                previous = self.object.get_previous_in_gallery()
                context['previous'] = previous
            except PhotoGroup.DoesNotExist:
                pass
        elif not self.object.is_public and self.object.owner.id == user.id:
            try:
                next = self.object.get_next_in_own_gallery()

                context['next'] = next
            except PhotoGroup.DoesNotExist:
                pass
            # Obtenemos la anterior imagen y comprobamos si pertenece a nuestra propiedad
            try:
                previous = self.object.get_previous_in_own_gallery()
                context['previous'] = previous
            except PhotoGroup.DoesNotExist:
                pass
        return context

    def user_pass_test(self):
        """
        Comprueba si un usuario tiene permisos
        para ver la galeria solicitada.
        """
        user = self.request.user
        if not self.object.is_public and user.id != self.object.owner.id:
            return False
        elif user.id == self.object.owner.id:
            return True

        try:
            user_profile = NodeProfile.nodes.get(title=self.username)
            n = NodeProfile.nodes.get(user_id=user.id)
        except NodeProfile.DoesNotExist:
            raise Http404

        visibility = user_profile.is_visible(n)

        if visibility and visibility != 'all':
            return False
        return True


@login_required()
def delete_video(request):
    """
    Eliminamos una video, comprobamos si el solicitante
    es el autor de la foto, si es asi, procedemos.
    """
    if request.method == 'DELETE':
        user = request.user
        _id = int(QueryDict(request.body).get('id'))
        video_to_delete = get_object_or_404(VideoGroup, id=_id)

        if user.pk == video_to_delete.owner_id:
            video_to_delete.delete()
            response_data = {}
            response_data['msg'] = '¡Video eliminado!.'
            response_data['author'] = user.username

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
