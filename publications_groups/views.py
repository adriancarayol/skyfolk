from bs4 import BeautifulSoup
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView
from publications.utils import parse_string
from publications_gallery.models import PublicationPhoto
from photologue.models import Photo
from publications.exceptions import EmptyContent
from publications_gallery.forms import PublicationPhotoForm
from publications.views import logger, get_or_create_csrf_token
from user_profile.models import NodeProfile
from utils.ajaxable_reponse_mixin import AjaxableResponseMixin
from emoji.models import Emoji


class PublicationGroupView(AjaxableResponseMixin, CreateView):
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
        super(PublicationGroupView, self).__init__()

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
                form.save_m2m()  # Saving tags
                publication.save(update_fields=['content'],
                                 new_comment=True, csrf_token=get_or_create_csrf_token(
                        self.request))  # Guardamos la publicacion si no hay errores

                return self.form_valid(form=form)
            except Exception as e:
                logger.info("Publication not created -> {}".format(e))
                return self.form_invalid(form=form, errors=e)
        return self.form_invalid(form=form)


publication_group_view = transaction.atomic(login_required(PublicationGroupView.as_view(), login_url='/'))