import io
import json
import logging
import os
import tempfile

import magic
from PIL import Image
from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import IntegrityError
from django.db import transaction
from django.http import HttpResponse
from django.http import JsonResponse
from django.middleware import csrf
from django.shortcuts import get_object_or_404, render, redirect, Http404
from django.views.generic.edit import CreateView
from django.core import serializers
from emoji import Emoji
from publications.forms import PublicationForm, SharedPublicationForm
from publications.models import Publication, PublicationImage, PublicationVideo
from user_profile.models import NodeProfile
from utils.ajaxable_reponse_mixin import AjaxableResponseMixin
from .exceptions import MaxFilesReached, SizeIncorrect, CantOpenMedia, MediaNotSupported, EmptyContent
from .tasks import process_video_publication, process_gif_publication
from .utils import get_author_avatar
from .utils import parse_string
from .utils import recursive_node_to_dict
from mptt.templatetags.mptt_tags import cache_tree_children
from django.db.models import Count

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
        raise CantOpenMedia(u'No podemos procesar el archivo {image}'.format(image=image.name))
    if image._size > settings.BACK_IMAGE_DEFAULT_SIZE:
        raise SizeIncorrect(
            u"Sólo se permiten archivos de hasta 5MB. ({image} tiene {size}B)".format(image=image.name,
                                                                                      size=image._size))


def check_num_images(image_collection):
    if len(image_collection) > 5:
        raise MaxFilesReached(u'Sólo se permiten 5 archivos por publicación.')


def _optimize_publication_media(instance, image_upload):
    check_num_images(image_upload)
    content_video = False
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
                        process_video_publication.delay(tmp.name, instance.id, media.name, user_id=instance.author.id,
                                board_owner_id=instance.board_owner_id)
                    content_video = True
                elif file_type[0] == "image" and file_type[1] == "gif":  # es un gif
                    tmp = tempfile.NamedTemporaryFile(suffix='.gif', delete=False)
                    for block in media.chunks():
                        tmp.write(block)
                    process_gif_publication.delay(tmp.name, instance.id, media.name, user_id=instance.author.id,
                            board_owner_id=instance.board_owner_id)
                    content_video = True
                else:  # es una imagen normal
                    try:
                        image = Image.open(media)
                    except IOError:
                        raise CantOpenMedia(u'No podemos procesar el archivo {image}'.format(image=media.name))
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
                raise MediaNotSupported(u'No podemos procesar este tipo de archivo {file}.'.format(file=media.name))
    return content_video


class PublicationNewView(AjaxableResponseMixin, CreateView):
    """
    Crear una publicacion para el perfil visitado.
    """
    form_class = PublicationForm
    model = Publication
    http_method_names = [u'post']
    success_url = '/thanks/'

    def __init__(self, **kwargs):
        super(PublicationNewView, self).__init__(**kwargs)
        self.object = None

    def post(self, request, *args, **kwargs):

        form_class = self.get_form_class()
        form = self.get_form(form_class)

        emitter = NodeProfile.nodes.get(user_id=self.request.user.id)
        print(request.POST)
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
                publication.author_id = emitter.user_id
                publication.board_owner_id = board_owner.user_id
                soup = BeautifulSoup(publication.content)  # Buscamos si entre los tags hay contenido
                for tag in soup.find_all(recursive=True):
                    if tag.text and not tag.text.isspace():
                        is_correct_content = True
                        break

                if not is_correct_content:  # Si el contenido no es valido, lanzamos excepcion

                    logger.info('Publicacion contiene espacios o no tiene texto')
                    raise EmptyContent('¡Comprueba el texto del comentario!')

                if publication.content.isspace():  # Comprobamos si el comentario esta vacio
                    raise EmptyContent('¡Comprueba el texto del comentario!')

                publication.save()  # Creamos publicacion
                publication.add_hashtag()  # add hashtags
                publication.parse_mentions()  # add mentions
                publication.parse_content()  # parse publication content
                publication.content = Emoji.replace(publication.content)  # Add emoji img
                form.save_m2m()  # Saving tags
                content_video = _optimize_publication_media(publication, request.FILES.getlist('image'))
                publication.save(update_fields=['content'],
                                 new_comment=True, csrf_token=get_or_create_csrf_token(
                        self.request))  # Guardamos la publicacion si no hay errores
                if not content_video:
                    return self.form_valid(form=form)
                else:
                    return self.form_valid(form=form,
                                           msg=u"Estamos procesando tus videos, te avisamos "
                                               u"cuando la publicación esté lista,")
            except Exception as e:
                logger.info("Publication not created -> {}".format(e))
                return self.form_invalid(form=form, errors=e)
        return self.form_invalid(form=form)


publication_new_view = login_required(PublicationNewView.as_view(), login_url='/')
publication_new_view = transaction.atomic(publication_new_view)


@login_required(login_url='/')
def publication_detail(request, publication_id):
    """
    Muestra el thread de una conversacion
    """
    user = request.user
    try:
        request_pub = Publication.objects \
                .select_related('author').get(id=publication_id, deleted=False)
        publication = request_pub.get_descendants(include_self=True) \
                .filter(deleted=False) \
                .prefetch_related('extra_content', 'images',
                                'videos', 'shared_publication__images',
                                'shared_publication__videos',
                                'shared_publication__extra_content',
                                'tags',
                                'shared_publication__author',
                                'shared_photo_publication__p_author',
                                'shared_photo_publication__images',
                                'shared_photo_publication__videos',
                                'shared_photo_publication__publication_photo_extra_content',
                                'user_give_me_like', 'user_give_me_hate') \
                                        .select_related('author',
                                                'board_owner', 'shared_publication',
                                                'parent', 'shared_photo_publication')

        shared_id = publication.values_list('id', flat=True)
        pubs_shared = Publication.objects.filter(shared_publication__id__in=shared_id, deleted=False).values('shared_publication__id')\
                .order_by('shared_publication__id')\
                .annotate(total=Count('shared_publication__id'))

        pubs_shared_with_me = Publication.objects.filter(shared_publication__id__in=shared_id, author__id=user.id, deleted=False).values('author__id', 'shared_publication__id')

    except ObjectDoesNotExist:
        raise Http404

    try:
        author = NodeProfile.nodes.get(user_id=request_pub.author_id)
        m = NodeProfile.nodes.get(user_id=user.id)
    except NodeProfile.DoesNotExist:
        return redirect('user_profile:profile', username=request_pub.board_owner.username)

    privacity = author.is_visible(m)

    if privacity and privacity != 'all':
        return redirect('user_profile:profile', username=request_pub.board_owner.username)

    context = {
        'pubs_shared': pubs_shared,
        'pubs_shared_with_me': pubs_shared_with_me,
        'publication_id': publication_id,
        'publication': publication,
        'publication_shared': SharedPublicationForm()
    }

    return render(request, "account/publication_detail.html", context)


@login_required(login_url='/')
@transaction.atomic
def delete_publication(request):
    logger.debug('>>>>>>>> PETICION AJAX BORRAR PUBLICACION')
    data = {
        'response': False,
        'shared_pub_id': None
    }
    if request.POST:
        # print request.POST['userprofile_id']
        # print request.POST['publication_id']
        user = request.user
        publication_id = request.POST['publication_id']
        logger.info('usuario: {} quiere eliminar publicacion: {}'.format(user.username, publication_id))
        # Comprobamos si existe publicacion y que sea de nuestra propiedad
        try:
            publication = Publication.objects.prefetch_related('extra_content').select_related('shared_publication').defer('content').get(id=publication_id)
        except ObjectDoesNotExist:
            return HttpResponse(json.dumps(data),
                                content_type='application/json'
                                )
        logger.info('publication_author: {} publication_board_owner: {} request.user: {}'.format(
            publication.author.username, publication.board_owner.username, user.username))

        # Borramos publicacion
        if user.id == publication.author.id or user.id == publication.board_owner.id:
            publication.deleted = True
            publication.save(update_fields=['deleted'])
            publication.get_descendants().update(deleted=True)
            if publication.has_extra_content():
                publication.extra_content.delete()
            shared_pub = publication.shared_publication
            data['shared_pub_id'] = shared_pub.id if shared_pub else None
            logger.info('Publication deleted: {}'.format(publication.id))

        data['response'] = True
    return HttpResponse(json.dumps(data),
                        content_type='application/json'
                        )


@login_required(login_url='/')
@transaction.atomic
def add_like(request):
    response = False
    statuslike = 0
    if request.method == 'POST':
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


@transaction.atomic
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
        publication.save(update_fields=['content', 'created'],
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

        if not publication.parent and not last_pub:
            publications = publication.get_descendants().filter(level__lte=1, deleted=False).prefetch_related('extra_content', 'images',
                                'videos', 'shared_publication__images',
                                'shared_publication__videos', 'shared_publication__extra_content', 'user_give_me_like', 'user_give_me_hate') \
                            .select_related('author',
                            'board_owner', 'shared_publication', 'parent', 'shared_photo_publication') \
                                                                                .annotate(likes_count=Count('user_give_me_like')) \
                                                                                .annotate(hates_count=Count('user_give_me_hate'))[:20]
        elif not publication.parent and last_pub:
            try:
                after_date = Publication.objects.filter(id=last_pub).values("created")
            except Publication.DoesNotExist:
                after_date = 0

            publications = publication.get_descendants().filter(level__lte=1, created__lte=after_date, deleted=False).exclude(id=last_pub).prefetch_related('extra_content', 'images',
                                'videos', 'shared_publication__images',
                                'shared_publication__videos', 'shared_publication__extra_content', 'user_give_me_like', 'user_give_me_hate') \
                            .select_related('author',
                            'board_owner', 'shared_publication', 'parent', 'shared_photo_publication') \
                                                                                .annotate(likes_count=Count('user_give_me_like')) \
                                                                                .annotate(hates_count=Count('user_give_me_hate'))[:20]
        elif publication.parent and not last_pub:
            publications = publication.get_descendants().filter(deleted=False).prefetch_related('extra_content', 'images',
                                'videos', 'shared_publication__images',
                                'shared_publication__videos', 'shared_publication__extra_content', 'user_give_me_like', 'user_give_me_hate') \
                            .select_related('author',
                            'board_owner', 'shared_publication', 'parent', 'shared_photo_publication') \
                                                                                .annotate(likes_count=Count('user_give_me_like')) \
                                                                                .annotate(hates_count=Count('user_give_me_hate'))[:20]
        elif publication .parent and last_pub:
            try:
                after_date = Publication.objects.filter(id=last_pub).values("created")
            except Publication.DoesNotExist:
                after_date = 0

            publications =  publication.get_descendants().filter(deleted=False, created__lte=after_date).exclude(id=last_pub).prefetch_related('extra_content', 'images',
                                'videos', 'shared_publication__images',
                                'shared_publication__videos', 'shared_publication__extra_content', 'user_give_me_like', 'user_give_me_hate') \
                            .select_related('author',
                            'board_owner', 'shared_publication', 'parent', 'shared_photo_publication') \
                                                                                .annotate(likes_count=Count('user_give_me_like')) \
                                                                                .annotate(hates_count=Count('user_give_me_hate'))[:20]

        shared_id = publications.values_list('id', flat=True)
        pubs_shared = Publication.objects.filter(shared_publication__id__in=shared_id).values('shared_publication__id')\
                .order_by('shared_publication__id')\
                .annotate(total=Count('shared_publication__id'))

        shared_pubs = {item['shared_publication__id']:item for item in pubs_shared}

        for row in publications:
            extra_c = None
            have_extra_content = row.has_extra_content()

            if have_extra_content:
                extra_c = row.extra_content

            try:
                shares_count = shared_pubs[row.id]['total']
            except KeyError:
                shares_count = 0

            list_responses.append({'content': row.content, 'created': naturaltime(row.created), 'id': row.id,
                                'author_username': row.author.username, 'user_id': user.id,
                                'author_id': row.author.id, 'board_owner_id': row.board_owner_id,
                                'event_type': row.event_type, 'extra_content': have_extra_content,
                                'descendants': row.get_descendants_not_deleted(),
                                'token': get_or_create_csrf_token(request),
                                'parent': True if row.parent else False,
                                'parent_author': row.parent.author.username,
                                'parent_avatar': get_author_avatar(row.parent.author_id),
                                'images': list(row.images.all().values('image')),
                                'videos': list(row.videos.all().values('video')),
                                'author_avatar': get_author_avatar(row.author_id),
                                'likes': row.likes_count, 'hates': row.hates_count,
                                'shares': shares_count})
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
                                                  created__lte=publication.created).exclude(id=pub_id) \
                                                          .prefetch_related('extra_content', 'images',
                                                                            'videos', 'shared_publication__images',
                                                                            'shared_publication__videos', 'shared_publication__extra_content',
                                                                            'user_give_me_like', 'user_give_me_hate') \
                                                                                    .select_related('author',
                                                                        'board_owner', 'shared_publication',
                                                                        'parent', 'shared_photo_publication') \
                                                                                .annotate(likes_count=Count('user_give_me_like')) \
                                                                                .annotate(hates_count=Count('user_give_me_hate'))[:20]

        shared_id = publications.values_list('id', flat=True)
        pubs_shared = Publication.objects.filter(shared_publication__id__in=shared_id).values('shared_publication__id')\
                .order_by('shared_publication__id')\
                .annotate(total=Count('shared_publication__id'))


        shared_pubs = {item['shared_publication__id']:item for item in pubs_shared}

        list_responses = []

        for row in publications:
            extra_c = None
            have_extra_content = row.has_extra_content()
            if have_extra_content:
                extra_c = row.extra_content

            shared_pub = row.shared_publication
            have_shared_publication = False
            if shared_pub:
                have_shared_publication = True

            shared_photo_pub = row.shared_photo_publication
            have_shared_photo_publication = False
            if shared_photo_pub:
                have_shared_photo_publication = True
            try:
                shares_count = shared_pubs[row.id]['total']
            except KeyError:
                shares_count = 0

            list_responses.append({'content': row.content, 'created': naturaltime(row.created), 'id': row.id,
                                   'author_username': row.author.username, 'user_id': user.id,
                                   'author_id': row.author.id, 'board_owner_id': row.board_owner_id,
                                   'author_avatar': get_author_avatar(row.author_id), 'level': row.level,
                                   'event_type': row.event_type, 'extra_content': have_extra_content,
                                   'descendants': row.get_children_count(), 'shared_pub': have_shared_publication,
                                   'shared_photo_pub': have_shared_photo_publication,
                                   'images': list(row.images.all().values('image')),
                                   'videos': list(row.videos.all().values('video')),
                                   'token': get_or_create_csrf_token(request),
                                   'likes': row.likes_count, 'hates': row.total_hates, 'shares': shares_count})
            if have_extra_content:
                list_responses[-1]['extra_content_title'] = extra_c.title
                list_responses[-1]['extra_content_description'] = extra_c.description
                list_responses[-1]['extra_content_image'] = extra_c.image
                list_responses[-1]['extra_content_url'] = extra_c.url

            if have_shared_publication:
                list_responses[-1]['shared_pub_id'] = shared_pub.pk
                list_responses[-1]['shared_pub_content'] = shared_pub.content
                list_responses[-1]['shared_pub_author'] = shared_pub.author.username
                list_responses[-1]['shared_pub_avatar'] = get_author_avatar(shared_pub.author_id)
                list_responses[-1]['shared_created'] = naturaltime(shared_pub.created)
                list_responses[-1]['shared_images'] = list(shared_pub.images.all().values('image'))
                list_responses[-1]['shared_videos'] = list(shared_pub.videos.all().values('video'))

                if shared_pub.has_extra_content():
                    list_responses[-1]['shared_pub_extra_title'] = shared_pub.extra_content.title
                    list_responses[-1][
                        'shared_pub_extra_description'] = shared_pub.extra_content.description
                    list_responses[-1][
                        'shared_pub_extra_image'] = shared_pub.extra_content.image if shared_pub.extra_content.image else None
                    list_responses[-1]['shared_pub_extra_url'] = shared_pub.extra_content.url

            if have_shared_photo_publication:
                list_responses[-1]['shared_photo_pub_id'] = shared_photo_pub.pk
                list_responses[-1]['shared_photo_pub_content'] = shared_photo_pub.content
                list_responses[-1]['shared_photo_pub_author'] = shared_photo_pub.p_author.username
                list_responses[-1]['shared_photo_pub_avatar'] = get_author_avatar(shared_photo_pub.p_author_id)
                list_responses[-1]['shared_photo_pub_created'] = naturaltime(shared_photo_pub.created)
                list_responses[-1]['shared_photo_pub_images'] = list(shared_photo_pub.images.all().values('image'))
                list_responses[-1]['shared_photo_pub_videos'] = list(shared_photo_pub.videos.all().values('video'))

                if shared_photo_pub.has_extra_content():
                    list_responses[-1]['shared_photo_pub_extra_title'] = shared_pub.publication_photo_extra_content.title
                    list_responses[-1][
                        'shared_photo_pub_extra_description'] = shared_pub.publication_photo_extra_content.description
                    list_responses[-1][
                        'shared_photo_pub_extra_image'] = shared_pub.publication_photo_extra_content.image if shared_pub.publication_photo_extra_content.image else None
                    list_responses[-1]['shared_photo_pub_extra_url'] = shared_pub.publication_photo_extra_content.url

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
            except ObjectDoesNotExist:
                response = False
                return HttpResponse(json.dumps(response), content_type='application/json')

            try:
                author = NodeProfile.nodes.get(user_id=pub_to_add.author_id)
                m = NodeProfile.nodes.get(user_id=user.id)
            except NodeProfile.DoesNotExist:
                return HttpResponse(json.dumps(response), content_type='application/json')

            privacity = author.is_visible(m)

            if privacity and privacity != 'all':
                return HttpResponse(json.dumps(response), content_type='application/json')

            shared = Publication.objects.filter(shared_publication_id=obj_pub, author_id=user.id,
                                                deleted=False).exists()

            if not shared:
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

                    pub = Publication.objects.create(
                        content='<i class="fa fa-share" aria-hidden="true"></i> Ha compartido de <a href="/profile/%s">@%s</a><br>%s' % (
                            pub_to_add.author.username, pub_to_add.author.username, pub_content),
                        shared_publication_id=pub_to_add.id,
                        author=user,
                        board_owner=user, event_type=6)
                else:
                    pub = Publication.objects.create(
                        content='<i class="fa fa-share" aria-hidden="true"></i> Ha compartido de <a href="/profile/%s">@%s</a>' % (
                            pub_to_add.author.username, pub_to_add.author.username),
                        shared_publication_id=pub_to_add.id,
                        author=user,
                        board_owner=user, event_type=6)

                pub.send_notification(csrf_token=get_or_create_csrf_token(
                        request))
                response = True
                status = 1  # Representa la comparticion de la publicacion
                logger.info('Compartido el comentario %d' % (pub_to_add.id))
                return HttpResponse(json.dumps({'response': response, 'status': status}),
                                    content_type='application/json')

            if shared:
                Publication.objects.filter(shared_publication_id=pub_to_add.id, author_id=user.id).delete()
                response = True
                status = 2  # Representa la eliminacion de la comparticion
                logger.info('Compartido el comentario %d' % (pub_to_add.id))
                return HttpResponse(json.dumps({'response': response, 'status': status}),
                                    content_type='application/json')

    return HttpResponse(json.dumps(response), content_type='application/json')



def publication_filter_by_time(request):
    response = False
    publications = None
    user = request.user
    if request.method == "POST":
        json_data = json.loads(request.body.decode('utf-8'))
        try:
            try:
                board_owner_id = int(json_data['board_owner'])
            except ValueError:
                return HttpResponse(json.dumps("No se encuentra el perfil seleccionado"), content_type='application/json')
        except KeyError:
            return HttpResponse(json.dumps("No se encuentra el perfil seleccionado"), content_type='application/json')

        try:
            owner = NodeProfile.nodes.get(user_id=board_owner_id)
            emitter = NodeProfile.nodes.get(user_id=user.id)
        except NodeProfile.DoesNotExist:
            return HttpResponse(json.dumps("No puedes ver este perfil"), content_type='application/json')

        privacity = owner.is_visible(emitter)

        if privacity and privacity != 'all':
            return HttpResponse(json.dumps("No puedes ver este perfil"), content_type='application/json')

        root_nodes = cache_tree_children(Publication.objects.filter(board_owner_id=board_owner_id, deleted=False, level__lte=0)[:20])
        dicts = []
        for n in root_nodes:
            dicts.append(recursive_node_to_dict(n))

        return HttpResponse(json.dumps(dicts, indent=2), content_type='application/json')
    return HttpResponse(json.dumps("Only POST METHOD"), content_type='application/json')

def publication_filter_by_like(request):
    response = False
    publications = None
    user = request.user
    if request.method == "POST":
        json_data = json.loads(request.body.decode('utf-8'))
        try:
            try:
                board_owner_id = int(json_data['board_owner'])
            except ValueError:
                return HttpResponse(json.dumps("No se encuentra el perfil seleccionado"), content_type='application/json')
        except KeyError:
            return HttpResponse(json.dumps("No se encuentra el perfil seleccionado"), content_type='application/json')

        try:
            owner = NodeProfile.nodes.get(user_id=board_owner_id)
            emitter = NodeProfile.nodes.get(user_id=user.id)
        except NodeProfile.DoesNotExist:
            return HttpResponse(json.dumps("No puedes ver este perfil"), content_type='application/json')

        privacity = owner.is_visible(emitter)

        if privacity and privacity != 'all':
            return HttpResponse(json.dumps("No puedes ver este perfil"), content_type='application/json')

        root_nodes = cache_tree_children(Publication.objects.annotate(likes=Count('user_give_me_like')) \
            .filter(board_owner_id=board_owner_id, deleted=False, level__lte=0).order_by('-likes')[:20])

        dicts = []
        for n in root_nodes:
            dicts.append(recursive_node_to_dict(n))

        return HttpResponse(json.dumps(dicts, indent=2), content_type='application/json')
    return HttpResponse(json.dumps("Only POST METHOD"), content_type='application/json')


def publication_filter_by_relevance(request):
    response = False
    publications = None
    user = request.user
    if request.method == "POST":
        json_data = json.loads(request.body.decode('utf-8'))
        try:
            try:
                board_owner_id = int(json_data['board_owner'])
            except ValueError:
                return HttpResponse(json.dumps("No se encuentra el perfil seleccionado"), content_type='application/json')
        except KeyError:
            return HttpResponse(json.dumps("No se encuentra el perfil seleccionado"), content_type='application/json')

        try:
            owner = NodeProfile.nodes.get(user_id=board_owner_id)
            emitter = NodeProfile.nodes.get(user_id=user.id)
        except NodeProfile.DoesNotExist:
            return HttpResponse(json.dumps("No puedes ver este perfil"), content_type='application/json')

        privacity = owner.is_visible(emitter)

        if privacity and privacity != 'all':
            return HttpResponse(json.dumps("No puedes ver este perfil"), content_type='application/json')

        root_nodes = cache_tree_children(Publication.objects.annotate(likes=Count('user_give_me_like')) \
            .filter(board_owner_id=board_owner_id, deleted=False, level__lte=0).order_by('-likes', '-created')[:20])

        dicts = []
        for n in root_nodes:
            dicts.append(recursive_node_to_dict(n))

        return HttpResponse(json.dumps(dicts, indent=2), content_type='application/json')
    return HttpResponse(json.dumps("Only POST METHOD"), content_type='application/json')

