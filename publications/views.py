import json
import logging
import io
import os
import magic
import tempfile

from bs4 import BeautifulSoup
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect, Http404
from django.views.generic.edit import CreateView
from django.http import JsonResponse
from photologue.models import Photo
from publications.forms import PublicationForm, PublicationPhotoForm, SharedPublicationForm
from publications.models import Publication, PublicationPhoto, SharedPublication, PublicationImage, PublicationVideo
from utils.ajaxable_reponse_mixin import AjaxableResponseMixin
from django.core.files.uploadedfile import InMemoryUploadedFile
from emoji import Emoji
from django.contrib.humanize.templatetags.humanize import naturaltime
from .utils import get_author_avatar
from django.db import transaction
from .utils import parse_string
from django.middleware import csrf
from PIL import Image
from user_profile.models import NodeProfile
from django.conf import settings
from .utils import generate_path_video
from .tasks import process_video_publication, process_gif_publication

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_or_create_csrf_token(request):
    token = request.META.get('CSRF_COOKIE', None)
    if token is None:
        token = csrf.get_token(request)
        request.META['CSRF_COOKIE'] = token
    request.META['CSRF_COOKIE_USED'] = True
    return token


def check_image_property(image):
    if not image:
        raise ValueError('Cant read image')
    if image._size > settings.BACK_IMAGE_DEFAULT_SIZE:
        raise ValueError("Image file too large ( > 1mb )")


def check_num_images(image_collection):
    if len(image_collection) > 5:
        raise ValueError('Size of image list is too large! ( > 5) ')


def _optimize_publication_media(instance, image_upload):
    check_num_images(image_upload)
    if image_upload:
        for index, media in enumerate(image_upload):
            check_image_property(media)
            f = magic.Magic(mime=True, uncompress=True)
            file_type = f.from_buffer(media.read(1024)).split('/')
            try:
                if file_type[0] == "video":  # es un video
                    if file_type[1] == 'mp4':
                        PublicationVideo.objects.create(publication=instance, video=media)
                    else:
                        tmp = tempfile.NamedTemporaryFile(delete=False)
                        for block in media.chunks():
                            tmp.write(block)
                        process_video_publication.delay(tmp.name, instance.id, instance.author.id)
                elif file_type[0] == "image" and file_type[1] == "gif":  # es un gif
                    tmp = tempfile.NamedTemporaryFile(suffix='.gif', delete=False)
                    for block in media.chunks():
                        tmp.write(block)
                    process_gif_publication.delay(tmp.name, instance.id, instance.author.id)
                else:  # es una imagen normal
                    try:
                        image = Image.open(media)
                    except IOError:
                        raise ValueError('Cant read image')
                    if image.mode != 'RGBA':
                        image = image.convert('RGBA')
                    image.thumbnail((800, 600), Image.ANTIALIAS)
                    output = io.BytesIO()
                    image.save(output, format='JPEG', optimize=True, quality=70)
                    output.seek(0)
                    photo = InMemoryUploadedFile(output, None, "%s.jpeg" % os.path.splitext(media.name)[0],
                                                 'image/jpeg', output.tell(), None)
                    PublicationImage.objects.create(publication=instance, image=photo)
            except IndexError:
                raise ValueError('Cant get type of file')


class PublicationNewView(AjaxableResponseMixin, CreateView):
    """
    Crear una publicacion para el perfil visitado.
    """
    form_class = PublicationForm
    model = Publication
    http_method_names = [u'post']
    success_url = '/thanks/'

    def post(self, request, *args, **kwargs):
        self.object = None

        form_class = self.get_form_class()
        form = self.get_form(form_class)

        emitter = NodeProfile.nodes.get(user_id=self.request.user.id)
        board_owner = NodeProfile.nodes.get(user_id=int(request.POST['board_owner']))

        privacity = board_owner.is_visible(emitter)

        if privacity and privacity != 'all':
            raise IntegrityError("No have permissions")

        is_correct_content = False
        logger.info('POST DATA: {} \n FILES: {}'.format(request.POST, request.FILES))
        logger.info('tipo emitter: {}'.format(type(emitter.title)))
        logger.info('tipo board_owner: {}'.format(type(board_owner.title)))

        if form.is_valid():
            try:
                publication = form.save(commit=False)
                publication.author = User.objects.get(id=emitter.user_id)
                publication.board_owner = User.objects.get(id=board_owner.user_id)

                soup = BeautifulSoup(publication.content)  # Buscamos si entre los tags hay contenido
                for tag in soup.find_all(recursive=True):
                    if tag.text and not tag.text.isspace():
                        is_correct_content = True
                        break

                if not is_correct_content:  # Si el contenido no es valido, lanzamos excepcion
                    logger.info('Publicacion contiene espacios o no tiene texto')
                    raise IntegrityError('El comentario esta vacio')

                if publication.content.isspace():  # Comprobamos si el comentario esta vacio
                    raise IntegrityError('El comentario esta vacio')

                publication.save()  # Creamos publicacion
                publication.add_hashtag()  # add hashtags
                publication.parse_mentions()  # add mentions
                publication.parse_content()  # parse publication content
                publication.content = Emoji.replace(publication.content)  # Add emoji img
                form.save_m2m()  # Saving tags
                _optimize_publication_media(publication, request.FILES.getlist('image'))
                publication.save(update_fields=['content'],
                                 new_comment=True, csrf_token=get_or_create_csrf_token(
                        self.request))  # Guardamos la publicacion si no hay errores

                return self.form_valid(form=form)
            except Exception as e:
                logger.info("Publication not created -> {}".format(e))

        logger.info("Invalid form")
        return self.form_invalid(form=form)


publication_new_view = login_required(PublicationNewView.as_view(), login_url='/')
publication_new_view = transaction.atomic(publication_new_view)


def publication_detail(request, publication_id):
    """
    Muestra el thread de una conversacion
    """
    user = request.user
    try:
        request_pub = Publication.objects.get(id=publication_id, deleted=False)
        publication = request_pub.get_descendants(include_self=True).filter(deleted=False)
    except ObjectDoesNotExist:
        return Http404

    try:
        author = NodeProfile.nodes.get(user_id=request_pub.author_id)
        m = NodeProfile.nodes.get(user_id=user.id)
    except NodeProfile.DoesNotExist:
        return redirect('user_profile:profile', username=request_pub.board_owner.username)

    privacity = author.is_visible(m)

    if privacity and privacity != 'all':
        return redirect('user_profile:profile', username=request_pub.board_owner.username)

    context = {
        'publication': publication,
        'publication_shared': SharedPublicationForm()
    }

    return render(request, "account/publication_detail.html", context)


class PublicationPhotoView(AjaxableResponseMixin, CreateView):
    """
    Crear una publicación para mi perfil.
    """
    form_class = PublicationPhotoForm
    model = PublicationPhoto
    http_method_names = [u'post']
    success_url = '/thanks/'

    def __init__(self):
        self.object = None
        super(PublicationPhotoView, self).__init__()

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        emitter = get_object_or_404(get_user_model(),
                                    pk=request.POST.get('p_author', None))

        photo = get_object_or_404(Photo, pk=request.POST.get('board_photo', None))
        publication = None
        logger.debug('POST DATA: {}'.format(request.POST))
        logger.debug('tipo emitter: {}'.format(type(emitter)))
        if form.is_valid():
            try:
                publication = form.save(commit=False)
                publication.author = emitter
                publication.board_photo = photo
                if publication.content.isspace():
                    raise IntegrityError('El comentario esta vacio')
                publication.save(new_comment=True)
                logger.debug('>>>> PUBLICATION: '.format(publication))

                return self.form_valid(form=form)
            except IntegrityError as e:
                logger.debug("views.py line 48 -> {}".format(e))

        return self.form_invalid(form=form)


publication_photo_view = login_required(PublicationPhotoView.as_view(), login_url='/')


@login_required(login_url='/')
@transaction.atomic
def delete_publication(request):
    logger.debug('>>>>>>>> PETICION AJAX BORRAR PUBLICACION')
    response = False
    if request.POST:
        # print request.POST['userprofile_id']
        # print request.POST['publication_id']
        user = request.user
        publication_id = request.POST['publication_id']
        logger.info('usuario: {} quiere eliminar publicacion: {}'.format(user.username, publication_id))
        # Comprobamos si existe publicacion y que sea de nuestra propiedad
        try:
            publication = Publication.objects.get(id=publication_id)
        except ObjectDoesNotExist:
            response = False
            return HttpResponse(json.dumps(response),
                                content_type='application/json'
                                )
        logger.info('publication_author: {} publication_board_owner: {} request.user: {}'.format(
            publication.author.username, publication.board_owner.username, user.username))

        # Borramos publicacion
        if user.id == publication.author.id or user.id == publication.board_owner.id:
            publication.deleted = True
            publication.save(update_fields=['deleted'])
            # Publication.objects.filter(parent=publication).update(deleted=True)
            publication.get_descendants().update(deleted=True)
            shared = publication.shared_publication  # Comprobamos si es un comentario de compartir
            if shared:
                shared.publication.save()
                shared.delete()
            extra_content = publication.extra_content
            if extra_content:
                extra_content.delete()
            logger.info('Publication deleted: {}'.format(publication.id))

        response = True
    return HttpResponse(json.dumps(response),
                        content_type='application/json'
                        )


@login_required(login_url='/')
@transaction.atomic
def add_like(request):
    response = False
    statuslike = 0
    if request.POST:
        user = request.user
        id_for_publication = request.POST['publication_id']  # Obtenemos el ID de la publicacion

        try:
            publication = Publication.objects.get(id=id_for_publication)  # Obtenemos la publicacion
        except ObjectDoesNotExist:
            data = json.dumps({'response': response, 'statuslike': statuslike})
            return HttpResponse(data, content_type='application/json')

        try:
            author = NodeProfile.nodes.get(user_id=publication.author_id)
            m = NodeProfile.nodes.get(user_id=user.id)
        except NodeProfile.DoesNotExist:
            data = json.dumps({'response': response, 'statuslike': statuslike})
            return HttpResponse(data, content_type='application/json')

        privacity = author.is_visible(m)

        if privacity and privacity != 'all':
            data = json.dumps({'response': response, 'statuslike': statuslike})
            return HttpResponse(data, content_type='application/json')

        # Mostrar los usuarios que han dado un me gusta a ese comentario
        logger.info("USUARIO DA LIKE")
        logger.info("(USUARIO PETICIÓN): " + user.username + " PK_ID -> " + str(user.pk))
        logger.info("(PERFIL DE USUARIO): " + publication.author.username + " PK_ID -> " + str(publication.author.pk))

        if user.pk != publication.author.pk:
            # Si el escritor del comentario
            # es el que pulsa el boton de like
            # no dejamos que incremente el contador
            in_like = False
            in_hate = False

            if user in publication.user_give_me_like.all():  # Usuario en lista de likes
                in_like = True

            if user in publication.user_give_me_hate.all():  # Usuario en lista de hate
                in_hate = True

            if in_like and in_hate:  # Si esta en ambas listas (situacion no posible)
                publication.user_give_me_like.remove(user)
                publication.user_give_me_hate.remove(user)
                logger.info("Usuario esta en ambas listas, eliminado usuario de ambas listas")

            if in_hate:  # Si ha dado antes unlike
                logger.info("Incrementando like")
                logger.info("Decrementando hate")
                try:
                    publication.user_give_me_hate.remove(user)  # remove from hates
                    publication.user_give_me_like.add(user)  # add to like
                    publication.save()
                    response = True
                    statuslike = 3

                except IntegrityError:
                    response = False
                    statuslike = 0

                data = json.dumps({'response': response, 'statuslike': statuslike})
                return HttpResponse(data, content_type='application/json')

            elif in_like:  # Si ha dado antes like
                logger.info("Decrementando like")
                try:
                    publication.user_give_me_like.remove(request.user)
                    publication.save()
                    response = True
                    statuslike = 2
                except IntegrityError:
                    response = False
                    statuslike = 0

                data = json.dumps({'response': response, 'statuslike': statuslike})
                return HttpResponse(data, content_type='application/json')

            else:  # Si no ha dado like ni unlike
                try:
                    publication.user_give_me_like.add(user)
                    publication.save()
                    response = True
                    statuslike = 1
                except IntegrityError:
                    response = False
                    statuslike = 0

        else:
            response = False
            statuslike = 0

    logger.info("Fin like comentario ---> Response" + str(response)
                + " Estado" + str(statuslike))

    data = json.dumps({'response': response, 'statuslike': statuslike})
    return HttpResponse(data, content_type='application/json')


@login_required(login_url='/')
@transaction.atomic
def add_hate(request):
    response = False
    statuslike = 0
    data = []
    if request.POST:
        user = request.user
        id_for_publication = request.POST['publication_id']  # Obtenemos el ID de la publicacion
        try:
            publication = Publication.objects.get(id=id_for_publication)  # Obtenemos la publicacion
        except ObjectDoesNotExist:
            data = json.dumps({'response': response, 'statuslike': statuslike})
            return HttpResponse(data, content_type='application/json')

        try:
            author = NodeProfile.nodes.get(user_id=publication.author_id)
            m = NodeProfile.nodes.get(user_id=user.id)
        except NodeProfile.DoesNotExist:
            data = json.dumps({'response': response, 'statuslike': statuslike})
            return HttpResponse(data, content_type='application/json')

        privacity = author.is_visible(m)

        if privacity and privacity != 'all':
            data = json.dumps({'response': response, 'statuslike': statuslike})
            return HttpResponse(data, content_type='application/json')

        # Mostrar los usuarios que han dado un me gusta a ese comentario
        logger.info("USUARIO DA HATE")
        logger.info("(USUARIO PETICIÓN): " + user.username)
        logger.info("(PERFIL DE USUARIO): " + publication.author.username)

        if user.pk != publication.author.pk:
            # Si el escritor del comentario
            # es el que pulsa el boton de like
            # no dejamos que incremente el contador
            # tampoco si el usuario ya ha dado like antes.
            in_like = False
            in_hate = False

            if user in publication.user_give_me_like.all():  # Usuario en lista de likes
                in_like = True

            if user in publication.user_give_me_hate.all():  # Usuario en lista de hate
                in_hate = True

            if in_like and in_hate:  # Si esta en ambas listas (situacion no posible)
                publication.user_give_me_like.remove(user)
                publication.user_give_me_hate.remove(user)
                logger.info("Usuario esta en ambas listas, eliminado usuario de ambas listas")

            if in_like:  # Si ha dado antes like
                logger.info("Incrementando hate")
                logger.info("Decrementando like")
                try:
                    publication.user_give_me_like.remove(user)  # remove from like
                    publication.user_give_me_hate.add(user)  # add to hate
                    publication.save()
                    response = True
                    statuslike = 3

                except IntegrityError:
                    response = False
                    statuslike = 0

                data = json.dumps({'response': response, 'statuslike': statuslike})
                return HttpResponse(data, content_type='application/json')

            elif in_hate:  # Si ha dado antes hate
                logger.info("Decrementando hate")
                try:
                    publication.user_give_me_hate.remove(request.user)
                    publication.save()
                    response = True
                    statuslike = 2
                except IntegrityError:
                    response = False
                    statuslike = 0

                data = json.dumps({'response': response, 'statuslike': statuslike})
                return HttpResponse(data, content_type='application/json')

            else:  # Si no ha dado like ni unlike
                try:
                    publication.user_give_me_hate.add(user)
                    publication.save()
                    response = True
                    statuslike = 1
                except IntegrityError:
                    response = False
                    statuslike = 0
        else:
            response = False
            statuslike = 0

    logger.info("Fin hate comentario ---> Response" + str(response)
                + " Estado" + str(statuslike))
    data = json.dumps({'response': response, 'statuslike': statuslike})
    return HttpResponse(data, content_type='application/json')


def edit_publication(request):
    """
    Permite al creador de la publicacion
    editar el contenido de la publicacion
    """
    if request.method == 'POST':
        user = request.user
        publication = get_object_or_404(Publication, id=request.POST['id'])

        if publication.author.id != user.id:
            return JsonResponse({'data': "No tienes permisos para editar este comentario"})

        if publication.event_type != 1 and publication.event_type != 3:
            return JsonResponse({'data': "No puedes editar este tipo de comentario"})

        publication.content = request.POST.get('content', None)

        publication.add_hashtag()  # add hashtags
        publication.parse_content()  # parse publication content
        is_correct_content = False
        soup = BeautifulSoup(publication.content)  # Buscamos si entre los tags hay contenido
        for tag in soup.find_all(recursive=True):
            if tag.text and not tag.text.isspace():
                is_correct_content = True
                break

        if not is_correct_content:  # Si el contenido no es valido, lanzamos excepcion
            logger.info('Publicacion contiene espacios o no tiene texto')
            raise IntegrityError('El comentario esta vacio')

        if publication.content.isspace():  # Comprobamos si el comentario esta vacio
            raise IntegrityError('El comentario esta vacio')

        publication.parse_mentions()  # add mentions
        publication.save(update_fields=['content', 'created', 'extra_content'],
                         new_comment=True, is_edited=True)  # Guardamos la publicacion si no hay errores

        return JsonResponse({'data': True})
    return JsonResponse({'data': "No puedes acceder a esta URL."})


@login_required(login_url='/')
def load_more_comments(request):
    """
    Carga respuestas de un comentario padre (carga comentarios hijos (nivel 1) de un comentario padre (nivel 0))
    o carga comentarios a respuestas (cargar comentarios descendientes (nivel > 1) de un comentario hijo (nivel 1))
    """
    data = {
        'response': False
    }
    if request.method == 'POST':
        user = request.user
        pub_id = request.POST.get('id', None)  # publicacion padre
        last_pub = request.POST.get('last_pub', None)  # Ultima publicacion add
        try:
            publication = Publication.objects.get(id=pub_id)
        except ObjectDoesNotExist:
            return JsonResponse(data)

        try:
            board_owner = NodeProfile.nodes.get(user_id=publication.board_owner_id)
            m = NodeProfile.nodes.get(user_id=user.id)
        except NodeProfile.DoesNotExist:
            return JsonResponse(data)

        privacity = board_owner.is_visible(m)

        if privacity and privacity != 'all':
            return JsonResponse(data)

        list_responses = []

        if not publication.parent:  # Si es publicacion padre, devolvemos solo sus hijos (nivel 1)
            if not last_pub:
                for row in publication.get_descendants().filter(level__lte=1, deleted=False)[:20]:
                    extra_c = row.extra_content
                    have_extra_content = False
                    if extra_c:
                        have_extra_content = True
                    list_responses.append({'content': row.content, 'created': naturaltime(row.created), 'id': row.id,
                                           'author_username': row.author.username, 'user_id': user.id,
                                           'author_id': row.author.id, 'board_owner_id': row.board_owner_id,
                                           'event_type': row.event_type, 'extra_content': have_extra_content,
                                           'descendants': row.get_children_count(),
                                           'token': get_or_create_csrf_token(request),
                                           'parent': True if row.parent else False,
                                           'parent_author': row.parent.author.username,
                                           'parent_avatar': get_author_avatar(row.parent.author_id),
                                           'images': list(row.images.all().values('image')),
                                           'author_avatar': get_author_avatar(row.author_id),
                                           'likes': row.total_likes, 'hates': row.total_hates,
                                           'shares': row.total_shares})
                    if have_extra_content:
                        list_responses[-1]['extra_content_title'] = extra_c.title
                        list_responses[-1]['extra_content_description'] = extra_c.description
                        list_responses[-1]['extra_content_image'] = extra_c.image
                        list_responses[-1]['extra_content_url'] = extra_c.url
            else:
                for row in publication.get_descendants().filter(level__lte=1, id__lt=last_pub, deleted=False)[:20]:
                    extra_c = row.extra_content
                    have_extra_content = False
                    if extra_c:
                        have_extra_content = True
                    list_responses.append({'content': row.content, 'created': naturaltime(row.created), 'id': row.id,
                                           'author_username': row.author.username, 'user_id': user.id,
                                           'author_id': row.author.id, 'board_owner_id': row.board_owner_id,
                                           'event_type': row.event_type, 'extra_content': have_extra_content,
                                           'descendants': row.get_children_count(),
                                           'token': get_or_create_csrf_token(request),
                                           'parent': True if row.parent else False,
                                           'parent_author': row.parent.author.username,
                                           'parent_avatar': get_author_avatar(row.parent.autho_id),
                                           'images': list(row.images.all().values('image')),
                                           'author_avatar': get_author_avatar(row.author_id),
                                           'likes': row.total_likes, 'hates': row.total_hates,
                                           'shares': row.total_shares
                                           })
                    if have_extra_content:
                        list_responses[-1]['extra_content_title'] = extra_c.title
                        list_responses[-1]['extra_content_description'] = extra_c.description
                        list_responses[-1]['extra_content_image'] = extra_c.image
                        list_responses[-1]['extra_content_url'] = extra_c.url
            data['pubs'] = json.dumps(list_responses)
        else:  # Si es publicacion respuesta, devolvemos todos los niveles
            if not last_pub:
                for row in publication.get_descendants().filter(deleted=False)[:20]:
                    extra_c = row.extra_content
                    have_extra_content = False
                    if extra_c:
                        have_extra_content = True
                    list_responses.append({'content': row.content, 'created': naturaltime(row.created), 'id': row.id,
                                           'author_username': row.author.username, 'user_id': user.id,
                                           'author_id': row.author.id, 'board_owner_id': row.board_owner_id,
                                           'event_type': row.event_type, 'extra_content': have_extra_content,
                                           'token': get_or_create_csrf_token(request),
                                           'parent': True if row.parent else False,
                                           'parent_author': row.parent.author.username,
                                           'parent_avatar': get_author_avatar(row.parent.author_id),
                                           'images': list(row.images.all().values('image')),
                                           'author_avatar': get_author_avatar(row.author_id), 'level': row.level,
                                           'likes': row.total_likes, 'hates': row.total_hates,
                                           'shares': row.total_shares
                                           })
                    if have_extra_content:
                        list_responses[-1]['extra_content_title'] = extra_c.title
                        list_responses[-1]['extra_content_description'] = extra_c.description
                        list_responses[-1]['extra_content_image'] = extra_c.image
                        list_responses[-1]['extra_content_url'] = extra_c.url
            else:
                for row in publication.get_descendants().filter(deleted=False, id__lt=last_pub)[:20]:
                    extra_c = row.extra_content
                    have_extra_content = False
                    if extra_c:
                        have_extra_content = True
                    list_responses.append({'content': row.content, 'created': naturaltime(row.created), 'id': row.id,
                                           'author_username': row.author.username, 'user_id': user.id,
                                           'author_id': row.author.id, 'board_owner_id': row.board_owner_id,
                                           'event_type': row.event_type, 'extra_content': have_extra_content,
                                           'token': get_or_create_csrf_token(request),
                                           'parent': True if row.parent else False,
                                           'parent_author': row.parent.author.username,
                                           'parent_avatar': get_author_avatar(row.parent.author_id),
                                           'images': list(row.images.all().values('image')),
                                           'author_avatar': get_author_avatar(row.author_id), 'level': row.level,
                                           'likes': row.total_likes, 'hates': row.total_hates,
                                           'shares': row.total_shares})
                    if have_extra_content:
                        list_responses[-1]['extra_content_title'] = extra_c.title
                        list_responses[-1]['extra_content_description'] = extra_c.description
                        list_responses[-1]['extra_content_image'] = extra_c.image
                        list_responses[-1]['extra_content_url'] = extra_c.url
            data['pubs'] = json.dumps(list_responses)
        data['response'] = True
    return JsonResponse(data)


@login_required(login_url='/')
def load_more_skyline(request):
    """
    Carga comentarios de nivel 0 en el skyline del perfil
    """
    data = {
        'response': False
    }
    if request.method == 'POST':
        user = request.user
        pub_id = request.POST.get('id', None)  # ultima publicacion en skyline
        try:
            publication = Publication.objects.get(id=pub_id)
        except ObjectDoesNotExist:
            return JsonResponse(data)

        try:
            board_owner = NodeProfile.nodes.get(user_id=publication.board_owner_id)
            m = NodeProfile.nodes.get(user_id=user.id)
        except NodeProfile.DoesNotExist:
            return JsonResponse(data)

        privacity = board_owner.is_visible(m)

        if privacity and privacity != 'all':
            return JsonResponse(data)

        publications = Publication.objects.filter(board_owner=publication.board_owner, deleted=False, parent=None,
                                                  id__lt=pub_id)[:20]
        list_responses = []

        for row in publications:
            extra_c = row.extra_content
            have_extra_content = False
            if extra_c:
                have_extra_content = True

            shared_pub = row.shared_publication
            have_shared_publication = False
            if shared_pub:
                have_shared_publication = True

            list_responses.append({'content': row.content, 'created': naturaltime(row.created), 'id': row.id,
                                   'author_username': row.author.username, 'user_id': user.id,
                                   'author_id': row.author.id, 'board_owner_id': row.board_owner_id,
                                   'author_avatar': get_author_avatar(row.author_id), 'level': row.level,
                                   'event_type': row.event_type, 'extra_content': have_extra_content,
                                   'descendants': row.get_children_count(), 'shared_pub': have_shared_publication,
                                   'images': list(row.images.all().values('image')),
                                   'token': get_or_create_csrf_token(request),
                                   'likes': row.total_likes, 'hates': row.total_hates, 'shares': row.total_shares})
            if have_extra_content:
                list_responses[-1]['extra_content_title'] = extra_c.title
                list_responses[-1]['extra_content_description'] = extra_c.description
                list_responses[-1]['extra_content_image'] = extra_c.image
                list_responses[-1]['extra_content_url'] = extra_c.url

            if have_shared_publication:
                list_responses[-1]['shared_pub_id'] = shared_pub.publication.pk
                list_responses[-1]['shared_pub_content'] = shared_pub.publication.content
                list_responses[-1]['shared_pub_author'] = shared_pub.publication.author.username
                list_responses[-1]['shared_pub_avatar'] = get_author_avatar(shared_pub.publication.author_id)
                list_responses[-1]['shared_created'] = naturaltime(shared_pub.publication.created)
                list_responses[-1][
                    'shared_image'] = shared_pub.publication.image.url if shared_pub.publication.image else None

                shared_pub_extra_c = shared_pub.publication.extra_content

                if shared_pub_extra_c:
                    list_responses[-1]['shared_pub_extra_title'] = shared_pub.publication.extra_content.title
                    list_responses[-1][
                        'shared_pub_extra_description'] = shared_pub.publication.extra_content.description
                    list_responses[-1][
                        'shared_pub_extra_image'] = shared_pub.publication.extra_content.image if shared_pub.publication.extra_content.image else None
                    list_responses[-1]['shared_pub_extra_url'] = shared_pub.publication.extra_content.url

        data['pubs'] = json.dumps(list_responses)
        data['response'] = True
    return JsonResponse(data)


@login_required(login_url='/')
@transaction.atomic
def share_publication(request):
    """
    Copia la publicacion de otro skyline
    y se comparte en el tuyo
    """
    response = False
    status = 0
    print('>>>>>>>>>>>>> PETITION AJAX ADD TO TIMELINE')
    if request.POST:
        obj_pub = request.POST.get('publication_id', None)
        user = request.user
        form = SharedPublicationForm(request.POST or None)

        if form.is_valid():
            try:
                pub_to_add = Publication.objects.get(pk=obj_pub)

                try:
                    author = NodeProfile.nodes.get(user_id=pub_to_add.author_id)
                    m = NodeProfile.nodes.get(user_id=user.id)
                except NodeProfile.DoesNotExist:
                    return HttpResponse(json.dumps(response), content_type='application/json')

                privacity = author.is_visible(m)

                if privacity and privacity != 'all':
                    return HttpResponse(json.dumps(response), content_type='application/json')

                shared, created = SharedPublication.objects.get_or_create(by_user=user, publication=pub_to_add)

                if created:
                    content = request.POST.get('content', None)

                    if content:

                        is_correct_content = False
                        pub_content = parse_string(content)  # Comprobamos que el comentario sea correcto
                        soup = BeautifulSoup(pub_content)  # Buscamos si entre los tags hay contenido
                        for tag in soup.find_all(recursive=True):
                            if tag.text and not tag.text.isspace():
                                is_correct_content = True
                                break

                        if not is_correct_content:  # Si el contenido no es valido, lanzamos excepcion
                            logger.info('Publicacion contiene espacios o no tiene texto')
                            raise IntegrityError('El comentario esta vacio')

                        if pub_content.isspace():  # Comprobamos si el comentario esta vacio
                            raise IntegrityError('El comentario esta vacio')

                        Publication.objects.create(
                            content='<i class="fa fa-share" aria-hidden="true"></i> Ha compartido de <a href="/profile/%s">@%s</a><br>%s' % (
                                pub_to_add.author.username, pub_to_add.author.username, pub_content),
                            shared_publication=shared,
                            author=user,
                            board_owner=user, event_type=6)
                    else:
                        Publication.objects.create(
                            content='<i class="fa fa-share" aria-hidden="true"></i> Ha compartido de <a href="/profile/%s">@%s</a>' % (
                                pub_to_add.author.username, pub_to_add.author.username), shared_publication=shared,
                            author=user,
                            board_owner=user, event_type=6)

                    pub_to_add.save()
                    response = True
                    status = 1  # Representa la comparticion de la publicacion
                    logger.info('Compartido el comentario %d' % (pub_to_add.id))
                    return HttpResponse(json.dumps({'response': response, 'status': status}),
                                        content_type='application/json')

                if not created and shared:
                    Publication.objects.get(shared_publication=shared).delete()
                    shared.delete()
                    pub_to_add.save()
                    response = True
                    status = 2  # Representa la eliminacion de la comparticion
                    logger.info('Compartido el comentario %d' % (pub_to_add.id))
                    return HttpResponse(json.dumps({'response': response, 'status': status}),
                                        content_type='application/json')

            except ObjectDoesNotExist:
                response = False

        return HttpResponse(json.dumps(response), content_type='application/json')
