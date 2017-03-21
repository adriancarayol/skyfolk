import json
import logging
import datetime

from bs4 import BeautifulSoup
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.views.generic.edit import CreateView
from el_pagination.views import AjaxListView
from django.http import JsonResponse
from photologue.models import Photo
from publications.forms import PublicationForm, PublicationPhotoForm, PublicationEdit
from publications.models import Publication, PublicationPhoto
from timeline.models import Timeline, EventTimeline
from user_profile.forms import SearchForm
from .forms import ReplyPublicationForm
from utils.ajaxable_reponse_mixin import AjaxableResponseMixin
from django.db import transaction
from emoji import Emoji
from django.contrib.humanize.templatetags.humanize import naturaltime
from .utils import get_author_avatar

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

                publication.add_hashtag()  # add hashtags
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


class PublicationDetailView(AjaxListView):
    """
    Vista extendida de una publicacion
    """
    context_object_name = "publications"
    template_name = "account/publication_detail.html"
    page_template = "account/publication_detail_entry.html"

    def __init__(self):
        self.publication = None
        super(PublicationDetailView, self).__init__()

    def dispatch(self, request, *args, **kwargs):
        self.publication = get_object_or_404(Publication, id=self.kwargs['publication_id'], deleted=False)
        if self.user_pass_test():
            return super(PublicationDetailView, self).dispatch(request, *args, **kwargs)
        else:
            return redirect('user_profile:profile', username=self.publication.author.username)

    def get_queryset(self):
        return Publication.objects.filter(parent=self.publication.pk, deleted=False).order_by('created')

    def get_context_data(self, **kwargs):
        context = super(PublicationDetailView, self).get_context_data(**kwargs)
        user = self.request.user
        initial = {'author': user.pk, 'board_owner': user.pk}
        context['publication'] = self.publication
        context['reply_publication_form'] = ReplyPublicationForm(initial=initial)
        context['publicationSelfForm'] = PublicationForm(initial=initial)
        context['searchForm'] = SearchForm()
        context['notifications'] = user.notifications.unread()
        return context

    def user_pass_test(self):
        """
        Comprueba si un usuario tiene permisos
        para ver la galeria solicitada.
        """
        user = self.request.user
        user_profile = self.publication.author.profile

        visibility = user_profile.is_visible(user.profile)

        if visibility == ("nothing" or "both" or "followers" or "block"):
            return False
        return True


publication_detail = login_required(PublicationDetailView.as_view(), login_url='/')


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
            logger.info('Publication deleted: {}'.format(publication.id))

        # Borramos timeline del comentario
        try:
            EventTimeline.objects.filter(publication=request.POST['publication_id']).delete()
        except ObjectDoesNotExist:
            pass

        response = True
    return HttpResponse(json.dumps(response),
                        content_type='application/json'
                        )


@login_required(login_url='/')
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

        # Mostrar los usuarios que han dado un me gusta a ese comentario
        logger.info("USUARIO DA LIKE")
        logger.info("(USUARIO PETICIÓN): " + user.username + " PK_ID -> " + str(user.pk))
        logger.info("(PERFIL DE USUARIO): " + publication.author.username + " PK_ID -> " + str(publication.author.pk))

        if user.pk != publication.author.pk and user not in publication.user_give_me_like.all() \
                and user not in publication.user_give_me_hate.all():
            # Si el escritor del comentario
            # es el que pulsa el boton de like
            # no dejamos que incremente el contador
            # tampoco si el usuario ya ha dado like antes.
            logger.info("Incrementando like")
            try:
                publication.user_give_me_like.add(request.user)  # add users like
                publication.save()
                response = True
                statuslike = 1

            except ObjectDoesNotExist:
                response = False
                statuslike = 0

        elif user.pk != publication.author.pk and user in publication.user_give_me_like.all() \
                and user not in publication.user_give_me_hate.all():
            logger.info("Decrementando like")
            try:
                publication.user_give_me_like.remove(request.user)
                publication.save()
                response = True
                statuslike = 2
            except ObjectDoesNotExist:
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

        # Mostrar los usuarios que han dado un me gusta a ese comentario
        logger.info("USUARIO DA HATE")
        logger.info("(USUARIO PETICIÓN): " + user.username)
        logger.info("(PERFIL DE USUARIO): " + publication.author.username)

        if user.pk != publication.author.pk and user not in publication.user_give_me_like.all() \
                and user not in publication.user_give_me_hate.all():
            # Si el escritor del comentario
            # es el que pulsa el boton de like
            # no dejamos que incremente el contador
            # tampoco si el usuario ya ha dado like antes.
            logger.debug("Incrementando hate")
            try:
                publication.user_give_me_hate.add(user)  # add users like
                publication.save()
                response = True
                statuslike = 1

            except ObjectDoesNotExist:
                response = False
                statuslike = 0
        elif user.pk != publication.author.pk and user in publication.user_give_me_hate.all() \
                and user not in publication.user_give_me_like.all():
            logger.debug("Decrementando hate")
            try:
                publication.user_give_me_hate.remove(user)
                publication.save()
                response = True
                statuslike = 2
            except ObjectDoesNotExist:
                response = False
                statuslike = 0
        else:
            response = False
            statuslike = 0
    logger.info("Fin like comentario ---> Response" + str(response)
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

        print(request.POST.get('content', None))
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
