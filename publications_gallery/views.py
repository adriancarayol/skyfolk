import json

from bs4 import BeautifulSoup
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render, HttpResponse
from django.views.generic import CreateView
from publications.utils import parse_string
from publications_gallery.models import PublicationPhoto
from photologue.models import Photo
from publications.exceptions import EmptyContent
from publications.forms import PublicationPhotoForm
from publications.forms import SharedPublicationForm
from publications.views import logger, get_or_create_csrf_token
from user_profile.models import NodeProfile
from utils.ajaxable_reponse_mixin import AjaxableResponseMixin
from publications.models import Publication

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
        PublicationPhoto.objects.rebuild()
        photo = get_object_or_404(Photo, id=request.POST.get('board_photo', None))

        emitter = NodeProfile.nodes.get(user_id=self.request.user.id)
        board_owner = NodeProfile.nodes.get(user_id=photo.owner_id)

        privacity = board_owner.is_visible(emitter)

        if privacity and privacity != 'all':
            raise IntegrityError("No have permissions")

        is_correct_content = False

        logger.debug('POST DATA: {}'.format(request.POST))
        logger.debug('tipo emitter: {}'.format(type(emitter)))
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
                # publication.add_hashtag()  # add hashtags
                # publication.parse_mentions()  # add mentions
                # publication.parse_content()  # parse publication content
                # publication.content = Emoji.replace(publication.content)  # Add emoji img
                form.save_m2m()  # Saving tags
                # content_video = _optimize_publication_media(publication, request.FILES.getlist('image'))
                publication.save(update_fields=['content'],
                                 new_comment=True, csrf_token=get_or_create_csrf_token(
                        self.request))  # Guardamos la publicacion si no hay errores
                # if not content_video:
                return self.form_valid(form=form)
                # else:
                # return self.form_valid(form=form,
                #                   msg=u"Estamos procesando tus videos, te avisamos "
                #                       u"cuando la publicación esté lista,")
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
        print(publication_id)
        request_pub = PublicationPhoto.objects.get(id=publication_id, deleted=False)
        publication = request_pub.get_descendants(include_self=True).filter(deleted=False)
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
        'publication': publication,
        'publication_shared': SharedPublicationForm()
    }

    return render(request, "account/publication_detail.html", context)


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
            # TODO: Descomentar lineas extra_content
            # extra_content = publication.extra_content
            # if extra_content:
            #     extra_content.delete()
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

        if user.pk != publication.p_author_id:
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

        if user.id != publication.p_author_id:
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

            shared = Publication.objects.filter(shared_photo_publication_id=obj_pub, author_id=user.id, deleted=False).exists()

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

                    Publication.objects.create(
                        content='<i class="fa fa-share" aria-hidden="true"></i> Ha compartido de <a href="/profile/%s">@%s</a><br>%s' % (
                            pub_to_add.p_author.username, pub_to_add.p_author.username, pub_content),
                        shared_photo_publication_id=pub_to_add.id,
                        author=user,
                        board_owner=user, event_type=6)
                else:
                    Publication.objects.create(
                        content='<i class="fa fa-share" aria-hidden="true"></i> Ha compartido de <a href="/profile/%s">@%s</a>' % (
                            pub_to_add.p_author.username, pub_to_add.p_author.username),
                        shared_photo_publication_id=pub_to_add.id,
                        author=user,
                        board_owner=user, event_type=6)

                response = True
                status = 1  # Representa la comparticion de la publicacion
                logger.info('Compartido el comentario %d' % (pub_to_add.id))
                return HttpResponse(json.dumps({'response': response, 'status': status}),
                                    content_type='application/json')

            if shared:
                Publication.objects.filter(shared_photo_publication_id=pub_to_add.id, author_id=user.id).delete()
                response = True
                status = 2  # Representa la eliminacion de la comparticion
                logger.info('Elimiando el comentario %d' % (pub_to_add.id))
                return HttpResponse(json.dumps({'response': response, 'status': status}),
                                    content_type='application/json')

    return HttpResponse(json.dumps(response), content_type='application/json')
