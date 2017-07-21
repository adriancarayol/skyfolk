import json

from bs4 import BeautifulSoup
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db import transaction
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, HttpResponse
from django.views.generic import CreateView
from publications.utils import parse_string
from publications_gallery.models import PublicationPhoto
from photologue.models import Photo
from publications.exceptions import EmptyContent
from publications_gallery.forms import PublicationPhotoForm
from publications_gallery.forms import SharedPhotoPublicationForm
from publications.views import logger, get_or_create_csrf_token
from user_profile.models import NodeProfile
from utils.ajaxable_reponse_mixin import AjaxableResponseMixin
from publications.models import Publication
from emoji.models import Emoji
from .utils import optimize_publication_media
from django.db.models import Count
from django.contrib.humanize.templatetags.humanize import naturaltime
from avatar.templatetags.avatar_tags import avatar

class PublicationPhotoView(AjaxableResponseMixin, CreateView):
    """
    Crear una publicación para una imagen de
    la galeria de un usuario.
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
        photo = get_object_or_404(Photo, id=request.POST.get('board_photo', None))

        emitter = NodeProfile.nodes.get(user_id=self.request.user.id)
        board_photo_owner = NodeProfile.nodes.get(user_id=photo.owner_id)

        privacity = board_photo_owner.is_visible(emitter)

        if privacity and privacity != 'all':
            raise IntegrityError("No have permissions")

        is_correct_content = False

        logger.debug('POST DATA: {}'.format(request.POST))
        logger.debug('tipo emitter: {}'.format(type(emitter)))
        if form.is_valid():
            try:
                publication = form.save(commit=False)
                publication.author_id = emitter.user_id
                publication.board_photo_id = photo.id

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
                content_video = optimize_publication_media(publication, request.FILES.getlist('image'))
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


publication_photo_view = login_required(PublicationPhotoView.as_view(), login_url='/')


def publication_detail(request, publication_id):
    """
    Muestra el thread de una conversacion
    """
    user = request.user
    try:
        request_pub = PublicationPhoto.objects.get(id=publication_id, deleted=False)
        publication = request_pub.get_descendants(include_self=True) \
                .filter(deleted=False) \
                .prefetch_related('publication_photo_extra_content', 'images',
                                'videos', 'user_give_me_like', 'user_give_me_hate', 'tags') \
                                        .select_related('p_author',
                                                'board_photo',
                                                'parent')
        pubs_id = publication.values_list('id', flat=True)
        pubs_shared = Publication.objects.filter(shared_photo_publication__id__in=pubs_id, deleted=False) \
                .values('shared_photo_publication__id')\
                .order_by('shared_photo_publication__id')\
                .annotate(total=Count('shared_photo_publication__id'))

        pubs_shared_with_me = Publication.objects.filter(shared_photo_publication__id__in=pubs_id, author__id=user.id, deleted=False).values('author__id', 'shared_photo_publication__id')


    except PublicationPhoto.DoesNotExist:
        raise Http404

    try:
        author = NodeProfile.nodes.get(user_id=request_pub.p_author_id)
        m = NodeProfile.nodes.get(user_id=user.id)
    except NodeProfile.DoesNotExist:
        return redirect('photologue:photo-list', username=request_pub.board_photo.owner.username)

    privacity = author.is_visible(m)

    if privacity and privacity != 'all':
        return redirect('user_profile:profile', username=request_pub.board_photo.owner.username)

    context = {
        'publication': list(publication),
        'publication_id': publication_id,
        'pubs_shared': pubs_shared,
        'pubs_shared_with_me': pubs_shared_with_me,
        'photo': request_pub.board_photo,
        'publication_shared': SharedPhotoPublicationForm()
    }

    return render(request, "photologue/publication_detail.html", context)


@login_required(login_url='/')
@transaction.atomic
def delete_publication(request):
    logger.debug('>>>>>>>> PETICION AJAX BORRAR PUBLICACION')
    response = False
    if request.POST:

        user = request.user
        publication_id = request.POST['publication_id']
        logger.info('usuario: {} quiere eliminar publicacion: {}'.format(user.username, publication_id))
        # Comprobamos si existe publicacion y que sea de nuestra propiedad
        try:
            publication = PublicationPhoto.objects.get(id=publication_id)
        except PublicationPhoto.DoesNotExist:
            response = False
            return HttpResponse(json.dumps(response),
                                content_type='application/json'
                                )
        logger.info('publication_author: {} publication_board_photo: {} request.user: {}'.format(
            publication.p_author.username, publication.board_photo, user.username))

        # Borramos publicacion
        if user.id == publication.p_author.id or user.id == publication.board_photo.owner_id:
            publication.deleted = True
            publication.save(update_fields=['deleted'])
            publication.get_descendants().update(deleted=True)
            if publication.has_extra_content():
                publication.publication_photo_extra_content.delete()
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
            publication = PublicationPhoto.objects.get(id=id_for_publication)  # Obtenemos la publicacion
        except PublicationPhoto.DoesNotExist:
            data = json.dumps({'response': response, 'statuslike': statuslike})
            return HttpResponse(data, content_type='application/json')

        try:
            author = NodeProfile.nodes.get(user_id=publication.p_author_id)
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
        logger.info(
            "(PERFIL DE USUARIO): " + publication.p_author.username + " PK_ID -> " + str(publication.p_author_id))

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
            publication = PublicationPhoto.objects.get(id=id_for_publication)  # Obtenemos la publicacion
        except PublicationPhoto.DoesNotExist:
            data = json.dumps({'response': response, 'statuslike': statuslike})
            return HttpResponse(data, content_type='application/json')

        try:
            author = NodeProfile.nodes.get(user_id=publication.p_author_id)
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
        logger.info("(PERFIL DE USUARIO): " + publication.p_author.username)

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
        form = SharedPhotoPublicationForm(request.POST or None)

        if form.is_valid():
            try:
                pub_to_add = PublicationPhoto.objects.get(pk=obj_pub)

            except PublicationPhoto.DoesNotExist:
                response = False
                return HttpResponse(json.dumps(response), content_type='application/json')

            try:
                author = NodeProfile.nodes.get(user_id=pub_to_add.p_author_id)
                m = NodeProfile.nodes.get(user_id=user.id)
            except NodeProfile.DoesNotExist:
                return HttpResponse(json.dumps(response), content_type='application/json')

            privacity = author.is_visible(m)

            if privacity and privacity != 'all':
                return HttpResponse(json.dumps(response), content_type='application/json')

            shared = Publication.objects.filter(shared_photo_publication_id=obj_pub, author_id=user.id,
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
                            pub_to_add.p_author.username, pub_to_add.p_author.username, pub_content),
                        shared_photo_publication_id=pub_to_add.id,
                        author=user,
                        board_owner=user, event_type=7)
                else:
                    pub = Publication.objects.create(
                        content='<i class="fa fa-share" aria-hidden="true"></i> Ha compartido de <a href="/profile/%s">@%s</a>' % (
                            pub_to_add.p_author.username, pub_to_add.p_author.username),
                        shared_photo_publication_id=pub_to_add.id,
                        author=user,
                        board_owner=user, event_type=7)

                pub.send_notification(csrf_token=get_or_create_csrf_token(
                        request))
                response = True
                status = 1  # Representa la comparticion de la publicacion
                logger.info('Compartido el comentario %d' % (pub_to_add.id))
                return HttpResponse(json.dumps({'response': response, 'status': status}),
                                    content_type='application/json')

            if shared:
                Publication.objects.filter(shared_photo_publication_id=pub_to_add.id, author_id=user.id).delete()
                response = True
                status = 2  # Representa la eliminacion de la comparticion
                logger.info('Eliminando el comentario %d' % (pub_to_add.id))
                return HttpResponse(json.dumps({'response': response, 'status': status}),
                                    content_type='application/json')

    return HttpResponse(json.dumps(response), content_type='application/json')


@transaction.atomic
def edit_publication(request):
    """
    Permite al creador de la publicacion
    editar el contenido de la publicacion
    """
    if request.method == 'POST':
        user = request.user
        publication = get_object_or_404(PublicationPhoto, id=request.POST['id'])

        if publication.p_author_id != user.id:
            return JsonResponse({'data': "No tienes permisos para editar este comentario"})

        if publication.event_type != 1 and publication.event_type != 3:
            return JsonResponse({'data': "No puedes editar este tipo de comentario"})

        publication.content = request.POST.get('content', None)

        publication.add_hashtag()  # add hashtags
        # publication.parse_content()  # parse publication content
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
def load_more_descendants(request):
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
            publication = PublicationPhoto.objects.get(id=pub_id)
        except ObjectDoesNotExist:
            return JsonResponse(data)

        try:
            board_owner = NodeProfile.nodes.get(user_id=publication.board_photo.owner_id)
            m = NodeProfile.nodes.get(user_id=user.id)
        except NodeProfile.DoesNotExist:
            return JsonResponse(data)

        privacity = board_owner.is_visible(m)

        if privacity and privacity != 'all':
            return JsonResponse(data)

        list_responses = []

        if not publication.parent and not last_pub:
            publications = publication.get_descendants().filter(level__lte=1, deleted=False).prefetch_related('publication_photo_extra_content', 'images',
                                'videos',
                                'user_give_me_like', 'user_give_me_hate', 'parent__p_author') \
                            .select_related('p_author',
                            'board_photo', 'parent') \
                                                                                .annotate(likes_count=Count('user_give_me_like')) \
                                                                                .annotate(hates_count=Count('user_give_me_hate'))[:20]
        elif not publication.parent and last_pub:
            try:
                after_date = PublicationPhoto.objects.filter(id=last_pub).values("created")
            except PublicationPhoto.DoesNotExist:
                after_date = 0

            publications = publication.get_descendants().filter(level__lte=1, created__lte=after_date, deleted=False).exclude(id=last_pub).prefetch_related('publication_photo_extra_content', 'images',
                                'videos',
                                'user_give_me_like', 'user_give_me_hate', 'parent__p_author') \
                            .select_related('p_author',
                            'board_photo', 'parent') \
                                                                                .annotate(likes_count=Count('user_give_me_like')) \
                                                                                .annotate(hates_count=Count('user_give_me_hate'))[:20]
        elif publication.parent and not last_pub:
            publications = publication.get_descendants().filter(deleted=False).prefetch_related('publication_photo_extra_content', 'images',
                                'videos',
                                'user_give_me_like', 'user_give_me_hate', 'parent__p_author') \
                            .select_related('p_author',
                            'board_photo', 'parent') \
                                                                                .annotate(likes_count=Count('user_give_me_like')) \
                                                                                .annotate(hates_count=Count('user_give_me_hate'))[:20]
        elif publication .parent and last_pub:
            try:
                after_date = PublicationPhoto.objects.filter(id=last_pub).values("created")
            except PublicationPhoto.DoesNotExist:
                after_date = 0

            publications =  publication.get_descendants().filter(deleted=False, created__lte=after_date).exclude(id=last_pub).prefetch_related('publication_photo_extra_content', 'images',
                                'videos', 'user_give_me_like', 'user_give_me_hate', 'parent__p_author') \
                            .select_related('p_author',
                            'board_photo', 'parent') \
                                                                                .annotate(likes_count=Count('user_give_me_like')) \
                                                                                .annotate(hates_count=Count('user_give_me_hate'))[:20]

        pubs_id = publications.values_list('id', flat=True)
        pubs_shared = Publication.objects.filter(shared_photo_publication__id__in=pubs_id).values('shared_photo_publication__id')\
                .order_by('shared_photo_publication')\
                .annotate(total=Count('shared_photo_publication'))
        pubs_shared_with_me = Publication.objects.filter(shared_photo_publication__id__in=pubs_id, author_id=user.id) \
                .values_list('shared_photo_publication__id', flat=True)
        shared_pubs = {item['shared_photo_publication__id']:item for item in pubs_shared}
        likes_with_me = PublicationPhoto.objects.filter(id__in=pubs_id, user_give_me_like__id=user.id).values_list('id', flat=True)
        hates_with_me = PublicationPhoto.objects.filter(id__in=pubs_id, user_give_me_hate__id=user.id).values_list('id', flat=True)
        for row in publications:
            extra_c = None
            have_extra_content = row.has_extra_content()

            if have_extra_content:
                extra_c = row.publication_photo_extra_content

            try:
                shares_count = shared_pubs[row.id]['total']
            except KeyError:
                shares_count = 0

            list_responses.append({'content': row.content, 'created': naturaltime(row.created), 'id': row.id,
                                'author_username': row.p_author.username, 'user_id': user.id,
                                'p_author_id': row.p_author_id, 'board_photo_id': row.board_photo_id,
                                'user_like': True if row.id in likes_with_me else False,
                                'user_hate': True if row.id in hates_with_me else False,
                                'user_shared': True if row.id in pubs_shared_with_me else False,
                                'event_type': row.event_type, 'extra_content': have_extra_content,
                                'descendants': row.get_descendants_not_deleted(),
                                'token': get_or_create_csrf_token(request),
                                'parent': True if row.parent else False,
                                'parent_author': row.parent.p_author.username,
                                'parent_avatar': avatar(row.parent.p_author),
                                'images': [i.image.url for i in row.images.all()],
                                'videos': [v.video.url for v in row.videos.all()],
                                'author_avatar': avatar(row.p_author),
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
def load_more_publications(request):
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
            publication = PublicationPhoto.objects.get(id=pub_id)
        except ObjectDoesNotExist:
            return JsonResponse(data)

        try:
            board_owner = NodeProfile.nodes.get(user_id=publication.board_photo.owner_id)
            m = NodeProfile.nodes.get(user_id=user.id)
        except NodeProfile.DoesNotExist:
            return JsonResponse(data)

        privacity = board_owner.is_visible(m)

        if privacity and privacity != 'all':
            return JsonResponse(data)

        publications = PublicationPhoto.objects.filter(board_photo_id=publication.board_photo_id, deleted=False, parent=None,
                                                  created__lte=publication.created).exclude(id=pub_id) \
                                                          .prefetch_related('publication_photo_extra_content', 'images',
                                                                            'videos',
                                                                            'user_give_me_like', 'user_give_me_hate', 'parent__p_author') \
                                                                                    .select_related('p_author',
                                                                        'board_photo',
                                                                        'parent') \
                                                                                .annotate(likes_count=Count('user_give_me_like')) \
                                                                                .annotate(hates_count=Count('user_give_me_hate'))[:20]

        pubs_id = publications.values_list('id', flat=True)
        pubs_shared = Publication.objects.filter(shared_photo_publication__id__in=pubs_id).values('shared_photo_publication__id')\
                .order_by('shared_photo_publication__id')\
                .annotate(total=Count('shared_photo_publication__id'))

        pubs_shared_with_me = Publication.objects.filter(shared_photo_publication__id__in=pubs_id, author_id=user.id) \
                .values_list('shared_photo_publication__id', flat=True)
        shared_pubs = {item['shared_photo_publication__id']:item for item in pubs_shared}
        likes_with_me = PublicationPhoto.objects.filter(id__in=pubs_id, user_give_me_like__id=user.id).values_list('id', flat=True)
        hates_with_me = PublicationPhoto.objects.filter(id__in=pubs_id, user_give_me_hate__id=user.id).values_list('id', flat=True)
        list_responses = []

        for row in publications:
            extra_c = None
            have_extra_content = row.has_extra_content()
            if have_extra_content:
                extra_c = row.publication_photo_extra_content

            try:
                shares_count = shared_pubs[row.id]['total']
            except KeyError:
                shares_count = 0

            list_responses.append({'content': row.content, 'created': naturaltime(row.created), 'id': row.id,
                                   'author_username': row.p_author.username, 'user_id': user.id,
                                   'user_like': True if row.id in likes_with_me else False,
                                   'user_hate': True if row.id in hates_with_me else False,
                                   'user_shared': True if row.id in pubs_shared_with_me else False,
                                   'author_id': row.p_author_id, 'board_photo_id': row.board_photo_id,
                                   'author_avatar': avatar(row.p_author), 'level': row.level,
                                   'event_type': row.event_type, 'extra_content': have_extra_content,
                                   'descendants': row.get_children_count(),
                                   'images': [i.image.url for i in row.images.all()],
                                   'videos': [v.video.url for v in row.videos.all()],
                                   'token': get_or_create_csrf_token(request),
                                   'likes': row.likes_count, 'hates': row.total_hates, 'shares': shares_count})
            if have_extra_content:
                list_responses[-1]['extra_content_title'] = extra_c.title
                list_responses[-1]['extra_content_description'] = extra_c.description
                list_responses[-1]['extra_content_image'] = extra_c.image
                list_responses[-1]['extra_content_url'] = extra_c.url

        data['pubs'] = json.dumps(list_responses)
        data['response'] = True
    return JsonResponse(data)
