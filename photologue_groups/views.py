import json

from PIL import Image
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.files import File
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.db.models import Count, Q, Case, When, Value, IntegerField
from django.http import Http404, HttpResponseForbidden
from django.http import JsonResponse
from django.http import QueryDict, HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.six import BytesIO
from django.views.generic.detail import DetailView
from el_pagination.decorators import page_template
from el_pagination.views import AjaxListView

from itertools import chain


from publications_gallery_groups.forms import PublicationPhotoForm, PublicationPhotoEdit, PublicationVideoEdit, \
    PublicationVideoForm
from publications.forms import SharedPublicationForm
from publications_gallery_groups.models import PublicationGroupMediaPhoto, PublicationGroupMediaVideo
from user_groups.decorators import user_can_view_group_info
from user_profile.models import RelationShipProfile, BLOCK

from utils.forms import get_form_errors
from .forms import UploadFormPhoto, EditFormPhoto, UploadZipForm, UploadFormVideo, EditFormVideo
from .models import PhotoGroup, VideoGroup
from user_groups.models import UserGroups


# Collection views
@login_required(login_url='accounts/login')
@page_template("photologue/photo_gallery_page.html")
def collection_list(request, slug,
                    tag_slug,
                    template='photologue_groups/photo_gallery.html',
                    extra_context=None):
    """
    Busca fotografias con tags muy parecidos o iguales
    :return => Devuelve una lista de fotos con un parecido:
    """

    user = request.user

    try:
        group = UserGroups.objects.get(slug=slug)
    except UserGroups.DoesNotExist:
        raise Http404

    # Para comprobar si tengo permisos para ver el contenido de la coleccion


    if not group.is_public and user.id != group.owner_id:
        is_member = user.user_groups.filter(id=group.id).exists()
        if not is_member:
            return redirect('user_groups:group-profile', groupname=group.slug)

    form = UploadFormPhoto()
    form_zip = UploadZipForm(request.POST, request.FILES, request=request)

    photos = PhotoGroup.objects.filter(group=group,
                                       tags__slug=tag_slug)
    videos = VideoGroup.objects.filter(group=group, tags__slug=tag_slug)

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

    @method_decorator(user_can_view_group_info)
    def dispatch(self, request, *args, **kwargs):
        slug = self.kwargs.pop('slug')

        try:
            self.object = UserGroups.objects.get(slug=slug)
        except UserGroups.DoesNotExist:
            raise Http404

        return super(PhotoListView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):

        photos = PhotoGroup.objects.filter(group=self.object).select_related('owner',
                                                                             'effect').prefetch_related(
            'tags')
        videos = VideoGroup.objects.filter(group=self.object).select_related('owner').prefetch_related(
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

            if not group.is_public and user.id != group.owner_id and not user.user_groups.filter(pk=pk).exists():
                return HttpResponseForbidden("No tienes permiso para subir una imagen al grupo {}".format(group.name))

            obj = form.save(commit=False)
            obj.owner = user
            obj.group_id = pk

            if 'image' in request.FILES:
                crop_image(obj, request)

            obj.save()
            form.save_m2m()  # Para guardar los tags de la foto

            data = {
                'result': True,
                'state': 200,
                'message': 'Success',
                'content': render_to_string(request=request, template_name='channels/new_photo_group_gallery.html',
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

            if not group.is_public and user.id != group.owner_id and not user.user_groups.filter(pk=pk).exists():
                return HttpResponseForbidden("No tienes permiso para subir una imagen al grupo {}".format(group.name))

            obj = form.save(commit=False)
            obj.owner = user
            obj.group_id = pk

            file = form.cleaned_data['video']

            if isinstance(file, str):
                with open(form.cleaned_data['video'], 'rb') as f:
                    obj.video.save("video.mp4", File(f), True)

            obj.save()
            form.save_m2m()  # Para guardar los tags de la foto

            data = {
                'result': True,
                'state': 200,
                'message': 'Success',
                'content': render_to_string(request=request, template_name='channels/new_video_group_gallery.html',
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

    try:
        im.seek(1)
    except EOFError:
        is_animated = False
    else:
        is_animated = True

    if is_animated:
        obj.image = image
        return

    im.seek(0)
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
            group_id = form.cleaned_data['group']

            try:
                group = UserGroups.objects.get(id=group_id)
            except UserGroups.DoesNotExist:
                raise Http404

            if not group.is_public and user.id != group.owner_id and not user.user_groups.filter(id=group.id).exists():
                return HttpResponseForbidden("No puedes subir una colección a este grupo.")

            form.save(request=request)
            return redirect(reverse('photologue_groups:photo-list', kwargs={'slug': group.slug }))
        else:
            # Cambiar por JsonResponse
            return JsonResponse({'response': False})
    else:
        # Cambiar por JsonResponse
        return JsonResponse({'response': False})


@login_required()
def delete_photo(request):
    """
    Eliminamos una foto, comprobamos si el solicitante
    es el autor de la foto, si es asi, procedemos.
    """
    if request.method == 'DELETE':
        user = request.user
        _id = int(QueryDict(request.body).get('id'))
        photo_to_delete = get_object_or_404(PhotoGroup.objects.select_related('group'), id=_id)

        if not photo_to_delete.group.is_public and user.id != photo_to_delete.group.owner_id:
            if not user.user_groups.filter(id=photo_to_delete.group.id).exists():
                return HttpResponseForbidden("No tienes permisos para eliminar esta imagen.")

        if user.pk == photo_to_delete.owner_id or photo_to_delete.group.owner_id == user.pk:
            photo_to_delete.delete()
            response_data = {}
            response_data['msg'] = '¡Imagen eliminada!.'
            response_data['url'] = reverse('photologue_groups:photo-list', kwargs={'slug': photo_to_delete.group.slug})

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
    user = request.user
    photo = get_object_or_404(PhotoGroup.objects.select_related('group'), id=photo_id)

    if not photo.group.is_public and user.id != photo.group.owner_id:
        if not user.user_groups.filter(id=photo.group.id).exists():
            return HttpResponseForbidden("No tienes permisos para eliminar esta imagen.")

    form = EditFormPhoto(request.POST or None, instance=photo)

    if form.is_valid():
        if photo.owner.pk == user.pk or photo.group.owner_id == user.pk:
            response_data = {'msg': 'Photo was edited!'}
            form.save()
        else:
            response_data = {'msg': 'You cant edit this photo.'}
            return HttpResponse(
                json.dumps(response_data),
                content_type="application/json"
            )
        return redirect(reverse('photologue_groups:photo-list', kwargs={'slug': photo.group.slug}))
    else:
        print(form.errors)
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
    user = request.user

    video = get_object_or_404(VideoGroup.objects.select_related('group'), id=video_id)

    if not video.group.is_public and user.id != video.group.owner_id:
        if not user.user_groups.filter(id=video.group.id).exists():
            return HttpResponseForbidden("No tienes permisos para eliminar esta imagen.")

    form = EditFormVideo(request.POST or None, instance=video)

    if form.is_valid():
        if video.owner.pk == user.pk or video.group.owner_id == user.pk:
            response_data = {'msg': '¡Video editado con éxito!'}
            form.save()
        else:
            response_data = {'msg': 'No puedes editar este vídeo.'}
            return HttpResponse(
                json.dumps(response_data),
                content_type="application/json"
            )
        return redirect(reverse('photologue_groups:photo-list', kwargs={'slug': video.group.slug}))
    else:
        return HttpResponse(
            json.dumps({'Nothing to see': 'This isnt happening'}),
            content_type='application/json')


class PhotoDetailView(DetailView):
    """
    Cogemos el parametro de la url (para mostrar los detalles de la foto)
    """
    template_name = 'photologue_groups/photo_detail.html'
    model = PhotoGroup

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object(PhotoGroup.objects.filter(slug=self.kwargs['slug']) \
                                      .select_related('owner', 'group') \
                                      .prefetch_related('tags'))

        if self.user_pass_test():
            return super(PhotoDetailView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect('user_groups:group-profile', groupname=self.object.group.slug)

    def get_context_data(self, **kwargs):
        context = super(PhotoDetailView, self).get_context_data(**kwargs)
        user = self.request.user
        page = self.request.GET.get('page', 1)

        users_not_blocked_me = RelationShipProfile.objects.filter(
            to_profile=user.profile, type=BLOCK).values('from_profile_id')

        paginator = Paginator(
            PublicationGroupMediaPhoto.objects.annotate(likes=Count('user_give_me_like'),
                                              hates=Count('user_give_me_hate'), have_like=Count(Case(
                    When(user_give_me_like=user, then=Value(1)),
                    output_field=IntegerField()
                )), have_hate=Count(Case(
                    When(user_give_me_hate=user, then=Value(1)),
                    output_field=IntegerField()
                ))).filter(
                ~Q(author__profile__in=users_not_blocked_me)
                & Q(board_photo_id=self.object.id),
                Q(level__lte=0) & Q(deleted=False)) \
                .prefetch_related('publication_group_multimedia_photo_extra_content', 'images', 'videos') \
                .select_related('author',
                                'board_photo', 'parent'), 10)

        try:
            publications = paginator.page(page)
        except PageNotAnInteger:
            publications = paginator.page(1)
        except EmptyPage:
            publications = paginator.page(paginator.num_pages)

        context['publications'] = publications

        if self.request.is_ajax():
            self.template_name = 'photologue_groups/publications_entries.html'
            return context

        initial_photo = {'author': user.pk, 'board_photo': self.object}

        context['form'] = EditFormPhoto(instance=self.object)
        context['publication_photo'] = PublicationPhotoForm(initial=initial_photo)
        context['publication_shared'] = SharedPublicationForm()
        context['publication_edit'] = PublicationPhotoEdit()

        # Obtenemos la siguiente imagen y comprobamos si pertenece a nuestra propiedad

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

        return context

    def user_pass_test(self):
        """
        Comprueba si un usuario tiene permisos
        para ver la galeria solicitada.
        """
        user = self.request.user

        if not self.object.group.is_public and self.object.group.owner_id != user.id:
            is_member = user.user_groups.filter(id=self.object.group.id)
            if not is_member:
                return False

        return True


# Video Views

class VideoDetailView(DetailView):
    """
    Cogemos el parametro de la url (para mostrar los detalles de la foto)
    """
    template_name = 'photologue_groups/videos/video_detail.html'
    model = VideoGroup

    def __init__(self):
        self.username = None
        super(VideoDetailView, self).__init__()

    def get_object(self, queryset=None):
        return get_object_or_404(VideoGroup.objects.select_related('owner').prefetch_related('tags'),
                                 slug=self.kwargs['slug'])

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.user_pass_test():
            return super(VideoDetailView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect('user_groups:group-profile', groupname=self.object.group.slug)

    def get_context_data(self, **kwargs):
        context = super(VideoDetailView, self).get_context_data(**kwargs)
        user = self.request.user
        page = self.request.GET.get('page', 1)

        users_not_blocked_me = RelationShipProfile.objects.filter(
            to_profile=user.profile, type=BLOCK).values('from_profile_id')

        paginator = Paginator(
            PublicationGroupMediaVideo.objects.annotate(likes=Count('user_give_me_like'),
                                              hates=Count('user_give_me_hate'), have_like=Count(Case(
                    When(user_give_me_like=user, then=Value(1)),
                    output_field=IntegerField()
                )), have_hate=Count(Case(
                    When(user_give_me_hate=user, then=Value(1)),
                    output_field=IntegerField()
                ))).filter(
                ~Q(author__profile__in=users_not_blocked_me)
                & Q(board_video_id=self.object.id),
                Q(level__lte=0) & Q(deleted=False)) \
                .prefetch_related('publication_group_multimedia_video_extra_content', 'images', 'videos') \
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
            self.template_name = 'photologue_groups/videos/publications_entries.html'
            return context

        initial_video = {'author': user.pk, 'board_video': self.object}
        context['form'] = EditFormVideo(instance=self.object)
        context['publication_video'] = PublicationVideoForm(initial=initial_video)
        context['publication_shared'] = SharedPublicationForm()
        context['publication_edit'] = PublicationVideoEdit()

        # Obtenemos la siguiente imagen y comprobamos si pertenece a nuestra propiedad

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

        return context

    def user_pass_test(self):
        """
        Comprueba si un usuario tiene permisos
        para ver la galeria solicitada.
        """
        user = self.request.user

        if not self.object.group.is_public and self.object.group.owner_id != user.id:
            is_member = user.user_groups.filter(id=self.object.group.id)
            if not is_member:
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
        video_to_delete = get_object_or_404(VideoGroup.objects.select_related('group'), id=_id)

        if not video_to_delete.group.is_public and user.id != video_to_delete.group.owner_id:
            if not user.user_groups.filter(id=video_to_delete.group.id).exists():
                return HttpResponseForbidden("No tienes permisos para eliminar este video.")

        if user.pk == video_to_delete.owner_id or video_to_delete.group.owner_id == user.pk:
            video_to_delete.delete()
            response_data = {}
            response_data = {}
            response_data['msg'] = '¡Video eliminado!.'
            response_data['url'] = reverse('photologue_groups:photo-list', kwargs={'slug': video_to_delete.group.slug})

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
