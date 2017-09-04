from bs4 import BeautifulSoup
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.generic import CreateView

from emoji.models import Emoji
from publications.exceptions import EmptyContent
from publications.views import logger
from publications_groups.forms import PublicationGroupForm
from publications_groups.models import PublicationGroup
from user_groups.models import UserGroups
from user_profile.models import NodeProfile
from utils.ajaxable_reponse_mixin import AjaxableResponseMixin


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
        print(request.POST)

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
                parent = publication.parent
                if parent:
                    author = NodeProfile.nodes.get(user_id=parent.author_id)
                    emitter_node = NodeProfile.nodes.get(user_id=emitter.id)
                    if author.bloq.is_connected(emitter_node):
                        raise PermissionDenied('El autor de la publicación te ha bloqueado')

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

                publication.parse_mentions()  # add mentions
                publication.parse_content()  # parse publication content
                publication.add_hashtag()  # add hashtags
                publication.content = Emoji.replace(publication.content)  # Add emoji img
                
                publication.save()  # Creamos publicacion
                return self.form_valid(form=form)
            except Exception as e:
                logger.info("Publication not created -> {}".format(e))
                return self.form_invalid(form=form, errors=e)
        return self.form_invalid(form=form)


publication_group_view = transaction.atomic(login_required(PublicationGroupView.as_view(), login_url='/'))

class DeletePublication(View):
    http_method_names = ['post', ]


    def post(self, request, **kwargs):
        user = request.user
        pub_id = request.POST.get('id', None)
        board_group_id = request.POST.get('board_group', None)
        response = 'error'

        if not pub_id or not board_group_id:
            return JsonResponse({'response': response})

        try:
            group = UserGroups.objects.get(group_ptr_id=board_group_id)
            publication = PublicationGroup.objects.get(id=pub_id, board_group_id=board_group_id)
        except ObjectDoesNotExist:
            return JsonResponse({'response': response})

        if publication.author_id == user.id or user.has_perm('delete_publication', group):
            try:
                with transaction.atomic(using="default"):
                    publication.deleted = True
                    publication.save(update_fields=['deleted'])
                    publication.get_descendants().update(deleted=True)
            except Exception as e:
                logger.info(e)
                return JsonResponse({'response': response})
            response = True
        return JsonResponse({'response': response})


delete_publication = login_required(DeletePublication.as_view(), login_url='/')
