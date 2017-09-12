import json

import magic
from bs4 import BeautifulSoup
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import IntegrityError
from django.db import transaction
from django.db.models import Count
from django.db.models import Q
from django.http import Http404, JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render, HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import CreateView

from emoji.models import Emoji
from photologue.models import Photo
from publications.exceptions import EmptyContent
from publications.models import Publication
from publications.views import logger
from publications_gallery.forms import PublicationPhotoForm, PublicationPhotoEdit
from publications.forms import SharedPublicationForm
from publications_gallery.models import PublicationPhoto
from user_profile.node_models import NodeProfile
from utils.ajaxable_reponse_mixin import AjaxableResponseMixin
from .utils import optimize_publication_media, check_num_images


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
                parent = publication.parent
                if parent:
                    parent_owner = parent.p_author_id
                    parent_node = NodeProfile.nodes.get(user_id=parent_owner)
                    if parent_node.bloq.is_connected(emitter):
                        raise IntegrityError('No have permissions')
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

                publication.parse_content()  # parse publication content
                publication.parse_mentions()  # add mentions
                publication.add_hashtag()  # add hashtags
                publication.content = Emoji.replace(publication.content)  # Add emoji img

                media = request.FILES.getlist('image')
                check_num_images(media)

                f = magic.Magic(mime=True, uncompress=True)
                exts = [f.from_buffer(x.read(1024)).split('/') for x in media]

                have_video = False
                if any(word in 'gif video' for word in set([item for sublist in exts for item in sublist])):
                    have_video = True

                try:
                    with transaction.atomic(using="default"):
                        publication.save()  # Creamos publicacion
                        form.save_m2m()  # Saving tags
                        transaction.on_commit(
                            lambda: optimize_publication_media(publication, media, exts))
                        transaction.on_commit(lambda: publication.send_notification(request, is_edited=False))
                except Exception as e:
                    raise ValidationError(e)

                if not have_video:
                    return self.form_valid(form=form)
                else:
                    return self.form_valid(form=form,
                                           msg=u"Estamos procesando tus videos, te avisamos "
                                               u"cuando la publicación esté lista.")
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
    page = request.GET.get('page', 1)
    try:
        request_pub = PublicationPhoto.objects.select_related('board_photo', ).get(id=publication_id, deleted=False)
        if not request_pub.board_photo.is_public and user.id != request_pub.board_photo.owner.id:
            return redirect('photologue:photo-list', username=request_pub.board_photo.owner.username)
    except ObjectDoesNotExist:
        raise Http404

    try:
        author = NodeProfile.nodes.get(user_id=request_pub.p_author_id)
        m = NodeProfile.nodes.get(user_id=user.id)
    except NodeProfile.DoesNotExist:
        return redirect('photologue:photo-list', username=request_pub.board_photo.owner.username)

    privacity = author.is_visible(m)

    if privacity and privacity != 'all':
        return redirect('user_profile:profile', username=request_pub.board_photo.owner.username)

    try:
        publication = request_pub.get_descendants(include_self=True) \
            .filter(deleted=False) \
            .prefetch_related('publication_photo_extra_content', 'images',
                              'videos', 'user_give_me_like', 'user_give_me_hate', 'tags') \
            .select_related('p_author',
                            'board_photo',
                            'parent')
    except Exception as e:
        raise Exception('No se pudo cargar los descendientes de: {}'.format(request_pub))

    paginator = Paginator(publication, 10)

    try:
        publication = paginator.page(page)
    except PageNotAnInteger:
        publication = paginator.page(1)
    except EmptyPage:
        publication = paginator.page(paginator.num_pages)

    try:
        pubs_id = publication.object_list.values_list('id', flat=True)
        pubs_shared = Publication.objects.filter(shared_photo_publication__id__in=pubs_id, deleted=False) \
            .values('shared_photo_publication__id') \
            .order_by('shared_photo_publication__id') \
            .annotate(total=Count('shared_photo_publication__id'))
        shared_pubs = {item['shared_photo_publication__id']: item.get('total', 0) for item in pubs_shared}
        pubs_shared_with_me = Publication.objects.filter(shared_photo_publication__id__in=pubs_id, author__id=user.id,
                                                         deleted=False) \
            .values_list('shared_photo_publication__id', flat=True)

    except Exception as e:
        logger.info('No se pudo obtener las publicaciones compartidas para la publicacion: {}'.format(request_pub))
        pubs_shared = None
        pubs_shared_with_me = []
        shared_pubs = {}

    context = {
        'publication': publication,
        'publication_id': publication_id,
        'pubs_shared': shared_pubs,
        'pubs_shared_with_me': pubs_shared_with_me,
        'photo': request_pub.board_photo,
        'publication_shared': SharedPublicationForm()
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
    print('>>>>>>>>>>>>> PETITION AJAX ADD TO TIMELINE')
    if request.POST:
        user = request.user
        form = SharedPublicationForm(request.POST or None)

        if form.is_valid():
            obj_pub = form.cleaned_data['pk']
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
                pub = form.save(commit=False)
                pub.parse_content()  # parse publication content
                pub.add_hashtag()
                pub.parse_mentions()  # add mentions
                pub.content = Emoji.replace(pub.content)
                pub.content = '<i class="material-icons blue1e88e5 left">format_quote</i> Ha compartido de <a ' \
                              'href="/profile/%s">@%s</a><br>%s' % (
                                  pub_to_add.p_author.username, pub_to_add.p_author.username, pub.content)
                pub.shared_photo_publication_id = pub_to_add.id
                pub.author = user
                pub.board_owner = user
                pub.event_type = 7
                try:
                    with transaction.atomic(using="default"):
                        pub.save()
                        transaction.on_commit(lambda: pub.send_notification(request))
                    response = True
                except IntegrityError as e:
                    logger.info(e)
                logger.info('Compartido el comentario %d' % pub_to_add.id)

            return HttpResponse(json.dumps(response), content_type='application/json')


class RemoveSharedPhotoPublication(View):
    model = Publication

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(RemoveSharedPhotoPublication, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        pk = request.POST.get('pk', None)
        user = request.user
        try:
            Publication.objects.filter(shared_photo_publication_id=pk, author_id=user.id, deleted=False).update(
                deleted=True)
        except ObjectDoesNotExist:
            raise Http404
        data = {
            'response': True,
        }
        return JsonResponse(data)


@transaction.atomic
def edit_publication(request):
    """
    Permite al creador de la publicacion
    editar el contenido de la publicacion
    """
    if request.method == 'POST':
        form = PublicationPhotoEdit(request.POST or None)

        if form.is_valid():
            content = form.cleaned_data['content']
            pk = form.cleaned_data['pk']
            user = request.user

            publication = get_object_or_404(PublicationPhoto, id=pk)

            if publication.p_author_id != user.id:
                return JsonResponse({'data': "No tienes permisos para editar este comentario"})

            if publication.event_type != 1 and publication.event_type != 3:
                return JsonResponse({'data': "No puedes editar este tipo de comentario"})

            try:
                publication.content = content
                publication.parse_content()  # parse publication content
                publication.add_hashtag()  # add hashtags
                publication.parse_mentions()
                publication.content = Emoji.replace(publication.content)
                publication._edited = True
                with transaction.atomic(using="default"):
                    publication.save()  # Guardamos la publicacion si no hay errores
                    transaction.on_commit(lambda: publication.send_notification(request, is_edited=True))
                return JsonResponse({'data': True})
            except IntegrityError:
                return JsonResponse({'data': False})
        else:
            return JsonResponse({'data': False})

    return JsonResponse({'data': "No puedes acceder a esta URL."})


@login_required(login_url='/')
def load_more_descendants(request):
    """
    Carga respuestas de un comentario padre (carga comentarios hijos (nivel 1) de un comentario padre (nivel 0))
    o carga comentarios a respuestas (cargar comentarios descendientes (nivel > 1) de un comentario hijo (nivel 1))
    """
    if request.is_ajax():
        user = request.user
        pub_id = request.GET.get('pubid', None)  # publicacion padre
        page = request.GET.get('page', 1)  # Ultima publicacion add

        print('PAGE: {}, PUB_ID: {}'.format(page, pub_id))
        try:
            publication = PublicationPhoto.objects.get(id=pub_id)
        except PublicationPhoto.DoesNotExist:
            return Http404

        try:
            board_owner = NodeProfile.nodes.get(user_id=publication.board_photo.owner_id)
            m = NodeProfile.nodes.get(user_id=user.id)
        except NodeProfile.DoesNotExist:
            raise Http404

        privacity = board_owner.is_visible(m)

        if privacity and privacity != 'all':
            return HttpResponseForbidden()

        if not publication.parent:
            pubs = publication.get_descendants().filter(~Q(p_author__profile__from_blocked__to_blocked=user.profile)
                                                        & Q(level__lte=1)
                                                        & Q(deleted=False))
        else:
            pubs = publication.get_descendants().filter(~Q(p_author__profile__from_blocked__to_blocked=user.profile)
                                                        & Q(deleted=False))

        pubs = pubs.prefetch_related('publication_photo_extra_content', 'images',
                                     'videos',
                                     'user_give_me_like', 'user_give_me_hate', 'parent__p_author') \
            .select_related('p_author',
                            'board_photo', 'parent') \
            .annotate(likes_count=Count('user_give_me_like')) \
            .annotate(hates_count=Count('user_give_me_hate'))

        paginator = Paginator(pubs, 10)

        try:
            publications = paginator.page(page)
        except PageNotAnInteger:
            publications = paginator.page(1)
        except EmptyPage:
            publications = paginator.page(paginator.num_pages)

        pubs_id = publications.object_list.values_list('id', flat=True)
        pubs_shared = Publication.objects.filter(shared_photo_publication__id__in=pubs_id).values(
            'shared_photo_publication__id') \
            .order_by('shared_photo_publication') \
            .annotate(total=Count('shared_photo_publication'))
        pubs_shared_with_me = Publication.objects.filter(shared_photo_publication__id__in=pubs_id, author_id=user.id) \
            .values_list('shared_photo_publication__id', flat=True)
        shared_pubs = {item['shared_photo_publication__id']: item.get('total', 0) for item in pubs_shared}

        context = {
            'pub_id': pub_id,
            'publications': publications,
            'pubs_shared': shared_pubs,
            'pubs_shared_with_me': pubs_shared_with_me,
            'photo': publication.board_photo
        }
        return render(request, 'photologue/ajax_load_replies.html', context=context)
    return HttpResponseForbidden()
