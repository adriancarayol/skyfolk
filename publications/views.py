import json
import logging
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import ListView
from django.views.generic.edit import CreateView

from photologue.models import Photo
from publications.forms import PublicationForm, PublicationPhotoForm
from publications.models import Publication, PublicationPhoto
from timeline.models import Timeline
from utils.ajaxable_reponse_mixin import AjaxableResponseMixin

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

        privacity = board_owner.profile.is_visible(self.request.user.profile, self.request.user.pk)

        if privacity and privacity != 'all':
            raise IntegrityError("No have permissions")

        publication = None
        logger.debug('POST DATA: {}'.format(request.POST))
        logger.debug('tipo emitter: {}'.format(type(emitter)))
        logger.debug('tipo board_owner: {}'.format(type(board_owner)))
        if form.is_valid():
            try:
                publication = form.save(commit=False)

                publication.author = emitter
                publication.board_owner = board_owner
                if publication.content.isspace():
                    raise IntegrityError('El comentario esta vacio')
                publication.save(new_comment=True)
                logger.debug('>>>> PUBLICATION: ')
                t, created = Timeline.objects.get_or_create(publication=publication, author=publication.author.profile,
                                                            profile=publication.board_owner.profile)
                return self.form_valid(form=form)
            except IntegrityError as e:
                logger.debug("views.py line 48 -> {}".format(e))

        return self.form_invalid(form=form)


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


class PublicationPhotoView(AjaxableResponseMixin, CreateView):
    """
    Crear una publicación para mi perfil.
    """
    form_class = PublicationPhotoForm
    model = PublicationPhoto
    http_method_names = [u'post']
    success_url = '/thanks/'

    def __init__(self, *args, **kwargs):
        super(PublicationPhotoView, self).__init__(*args, **kwargs)
        self.object = None

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
            logger.info('Publication deleted: {}'.format(publication.id))

        # Borramos timeline del comentario
        try:
            Timeline.objects.get(publication__pk=request.POST['publication_id']).delete()
        except ObjectDoesNotExist:
            pass

        response = True
    return HttpResponse(json.dumps(response),
                        content_type='application/json'
                        )


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
