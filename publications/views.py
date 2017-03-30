import json
import logging
import datetime

from bs4 import BeautifulSoup
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect, Http404
from django.views.generic.edit import CreateView
from django.http import JsonResponse
from photologue.models import Photo
from publications.forms import PublicationForm, PublicationPhotoForm, PublicationEdit, SharedPublicationForm
from publications.models import Publication, PublicationPhoto, SharedPublication
from user_profile.forms import SearchForm
from .forms import ReplyPublicationForm
from utils.ajaxable_reponse_mixin import AjaxableResponseMixin
from emoji import Emoji
from django.contrib.humanize.templatetags.humanize import naturaltime
from .utils import get_author_avatar
from django.db import transaction
from .utils import parse_string

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
        # form = PublicationForm(request.POST)
        form = self.get_form()
        emitter = get_object_or_404(get_user_model(),
                                    pk=request.POST['author'])

        if emitter.pk != self.request.user.pk:
            raise IntegrityError("No have permissions.")

        board_owner = get_object_or_404(get_user_model(),
                                        pk=request.POST['board_owner'])

        privacity = board_owner.profile.is_visible(self.request.user.profile)

        if privacity and privacity != 'all':
            raise IntegrityError("No have permissions")

        publication = None
        is_correct_content = False
        logger.debug('POST DATA: {}'.format(request.POST))
        logger.debug('tipo emitter: {}'.format(type(emitter)))
        logger.debug('tipo board_owner: {}'.format(type(board_owner)))
        if form.is_valid():
            try:
                publication = form.save(commit=False)

                publication.author = emitter
                publication.board_owner = board_owner

                publication.parse_content()  # parse publication content

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
                publication.parse_mentions()  # add mentions
                publication.content = Emoji.replace(publication.content)
                publication.add_hashtag()  # add hashtags
                publication.save(update_fields=['content'],
                                 new_comment=True)  # Guardamos la publicacion si no hay errores

                logger.debug('>>>> PUBLICATION: ')

                return self.form_valid(form=form)
            except Exception as e:
                logger.debug("views.py line 48 -> {}".format(e))

        return self.form_invalid(form=form)


publication_new_view = login_required(PublicationNewView.as_view(), login_url='/')
publication_new_view = transaction.atomic(publication_new_view)

# TODO: Esto no es necesario, creo que con pagination queda solucionado
"""
class PublicationsListView(AjaxableResponseMixin, ListView):
    model = Publication
    template_name = 'account/tab-comentarios.html'
    http_method_names = ['get']
    ordering = ['-created']
    allow_empty = True
    context_object_name = 'publication_list'
    paginate_by = 1
    queryset = Publication.objects.all()

    def get_queryset(self):
        print(self.request.GET.get('type'))
        if self.request.GET.get('type') == 'reply':
            # TODO: pasar el resto de parametros por get
            self.template_name = 'account/tab-comentarios.html'
            return Publication.objects.get_publication_replies(
                self.request.GET.get('user_pk'),
                self.request.GET.get('booar_owner'),
                self.request.GET.get('parent'))
        else:
            return self.queryset
"""


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

    privacity = request_pub.author.profile.is_visible(user.profile)

    if privacity and privacity != 'all':
        return redirect('user_profile:profile', username=request_pub.board_owner.username)

    context = {
        'publication': publication
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
                shared.publication.shared -= 1
                shared.publication.save()
                shared.delete()
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

        privacity = publication.author.profile.is_visible(user.profile)

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
                    publication.hated -= 1
                    publication.liked += 1
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
                    publication.liked -= 1
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
                    publication.liked += 1
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

        privacity = publication.author.profile.is_visible(user.profile)

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
                    publication.liked -= 1
                    publication.hated += 1
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
                    publication.hated -= 1
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
                    publication.hated += 1
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

        if publication.event_type != 1:
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

        publication.save()  # Creamos publicacion
        publication.parse_mentions()  # add mentions
        publication.created = datetime.datetime.now()
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
        privacity = publication.board_owner.profile.is_visible(user.profile)

        if privacity and privacity != 'all':
            return JsonResponse(data)

        list_responses = []

        if not publication.parent:  # Si es publicacion padre, devolvemos solo sus hijos (nivel 1)
            if not last_pub:
                for row in publication.get_descendants().filter(level__lte=1, deleted=False)[:20]:
                    list_responses.append({'content': row.content, 'created': naturaltime(row.created), 'id': row.id,
                                           'author_username': row.author.username, 'user_id': user.id,
                                           'author_avatar': get_author_avatar(row.author)})
            else:
                for row in publication.get_descendants().filter(level__lte=1, id__lt=last_pub, deleted=False)[:20]:
                    list_responses.append({'content': row.content, 'created': naturaltime(row.created), 'id': row.id,
                                           'author_username': row.author.username, 'user_id': user.id,
                                           'author_avatar': get_author_avatar(row.author)})
            data['pubs'] = json.dumps(list_responses)
        else:  # Si es publicacion respuesta, devolvemos todos los niveles
            if not last_pub:
                for row in publication.get_descendants().filter(deleted=False)[:20]:
                    list_responses.append({'content': row.content, 'created': naturaltime(row.created), 'id': row.id,
                                           'author_username': row.author.username, 'user_id': user.id,
                                           'author_avatar': get_author_avatar(row.author), 'level': row.level})
            else:
                for row in publication.get_descendants().filter(deleted=False, id__lt=last_pub)[:20]:
                    list_responses.append({'content': row.content, 'created': naturaltime(row.created), 'id': row.id,
                                           'author_username': row.author.username, 'user_id': user.id,
                                           'author_avatar': get_author_avatar(row.author), 'level': row.level})
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

        privacity = publication.board_owner.profile.is_visible(user.profile)

        if privacity and privacity != 'all':
            return JsonResponse(data)

        publications = Publication.objects.filter(board_owner=publication.board_owner, deleted=False, parent=None,
                                                  id__lt=pub_id)[:20]
        list_responses = []

        for row in publications:
            list_responses.append({'content': row.content, 'created': naturaltime(row.created), 'id': row.id,
                                   'author_username': row.author.username, 'user_id': user.id,
                                   'author_avatar': get_author_avatar(row.author), 'level': row.level})

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

                if pub_to_add.author == user:
                    return HttpResponse(json.dumps(response), content_type='application/json')

                privacity = pub_to_add.author.profile.is_visible(user.profile)

                if privacity and privacity != 'all':
                    return HttpResponse(json.dumps(response), content_type='application/json')

                shared, created = SharedPublication.objects.get_or_create(by_user=user, publication=pub_to_add)

                if created:
                    content = request.POST.get('content', None)

                    if content:

                        is_correct_content = False
                        pub_content = parse_string(content) # Comprobamos que el comentario sea correcto
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
                                pub_to_add.author.username, pub_to_add.author.username, pub_content), shared_publication=shared,
                            author=user,
                            board_owner=user, event_type=6)
                    else:
                        Publication.objects.create(
                            content='<i class="fa fa-share" aria-hidden="true"></i> Ha compartido de <a href="/profile/%s">@%s</a>' % (
                                pub_to_add.author.username, pub_to_add.author.username), shared_publication=shared, author=user,
                            board_owner=user, event_type=6)

                    pub_to_add.shared += 1
                    pub_to_add.save()
                    response = True
                    status = 1 # Representa la comparticion de la publicacion
                    logger.info('Compartido el comentario %d -> %d veces' % (pub_to_add.id, pub_to_add.shared))
                    return HttpResponse(json.dumps({'response': response, 'status': status}), content_type='application/json')

                if not created and shared:
                    Publication.objects.get(shared_publication=shared).delete()
                    pub_to_add.shared -= 1
                    shared.delete()
                    pub_to_add.save()
                    response = True
                    status = 2 # Representa la eliminacion de la comparticion
                    logger.info('Compartido el comentario %d -> %d veces' % (pub_to_add.id, pub_to_add.shared))
                    return HttpResponse(json.dumps({'response': response, 'status': status}), content_type='application/json')

            except ObjectDoesNotExist:
                response = False

        return HttpResponse(json.dumps(response), content_type='application/json')
