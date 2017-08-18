from bs4 import BeautifulSoup
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView
from publications.utils import parse_string
from publications_groups.forms import PublicationGroupForm
from user_groups.models import UserGroups
from publications_groups.models import PublicationGroup
from publications.exceptions import EmptyContent
from publications_gallery.forms import PublicationPhotoForm
from publications.views import logger, get_or_create_csrf_token
from django.contrib.auth.models import User, Group
from utils.ajaxable_reponse_mixin import AjaxableResponseMixin
from emoji.models import Emoji


class PublicationGroupView(AjaxableResponseMixin, CreateView):
    """
    Crear una publicación para una imagen de
    la galeria de un usuario.
    """
    form_class = PublicationGroupForm
    model = PublicationGroup
    http_method_names = [u'post']
    success_url = '/thanks/'

    def __init__(self):
        self.object = None
        super(PublicationGroupView, self).__init__()

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        group = get_object_or_404(UserGroups, id=request.POST.get('board_group', None))
        emitter = User.objects.get(id=self.request.user.id)

        if group.owner.id != emitter.id:
            can_publish = emitter.has_perm('can_publish', group)
            if not can_publish:
                return self.form_invalid(form=form)

        is_correct_content = False

        if form.is_valid():
            try:
                publication = form.save(commit=False)
                publication.author_id = emitter.id
                publication.board_group_id = group.id

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
                return self.form_valid(form=form)
            except Exception as e:
                logger.info("Publication not created -> {}".format(e))
                return self.form_invalid(form=form, errors=e)
        return self.form_invalid(form=form)


publication_group_view = transaction.atomic(login_required(PublicationGroupView.as_view(), login_url='/'))
