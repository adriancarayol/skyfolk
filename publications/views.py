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
from django.contrib.contenttypes.models import ContentType
from django.contrib.humanize.templatetags.humanize import naturaltime, intword
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import IntegrityError
from django.db import transaction
from django.db.models import Count, Q, When, Value, IntegerField, Case, OuterRef, Subquery
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.middleware import csrf
from django.shortcuts import get_object_or_404, render, redirect, Http404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic.edit import CreateView
from mptt.templatetags.mptt_tags import cache_tree_children

from avatar.templatetags.avatar_tags import avatar_url
from emoji import Emoji
from notifications.models import Notification
from user_profile.models import RelationShipProfile, BLOCK, Profile
from .forms import PublicationForm, SharedPublicationForm, PublicationEdit
from .models import Publication, PublicationImage, PublicationVideo, ExtraContent
from user_profile.node_models import NodeProfile
from utils.ajaxable_reponse_mixin import AjaxableResponseMixin
from .exceptions import MaxFilesReached, SizeIncorrect, CantOpenMedia, MediaNotSupported, EmptyContent
from .tasks import process_video_publication, process_gif_publication
from latest_news.tasks import send_to_stream

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


def _optimize_publication_media(instance, image_upload, exts):
    if image_upload:
        for index, media in enumerate(image_upload):
            try:
                if exts[index][0] == "video":  # es un video
                    if exts[index][1] == 'mp4':
                        PublicationVideo.objects.create(publication=instance, video=media)
                    else:
                        tmp = tempfile.NamedTemporaryFile(delete=False)
                        for block in media.chunks():
                            tmp.write(block)
                        process_video_publication.delay(tmp.name, instance.id, media.name, user_id=instance.author.id,
                                                        board_owner_id=instance.board_owner_id)

                elif exts[index][0] == "image" and exts[index][1] == "gif":  # es un gif
                    tmp = tempfile.NamedTemporaryFile(suffix='.gif', delete=False)
                    for block in media.chunks():
                        tmp.write(block)
                    process_gif_publication.delay(tmp.name, instance.id, media.name, user_id=instance.author.id,
                                                  board_owner_id=instance.board_owner_id)

                else:  # es una imagen normal
                    try:
                        image = Image.open(media).convert('RGBA')
                    except IOError:
                        raise CantOpenMedia(u'No podemos procesar el archivo {image}'.format(image=media.name))

                    fill_color = (255, 255, 255, 0)

                    if image.mode in ('RGBA', 'LA'):
                        background = Image.new(image.mode[:-1], image.size, fill_color)
                        background.paste(image, image.split()[-1])
                        image = background

                    image.thumbnail((800, 600), Image.ANTIALIAS)
                    output = io.BytesIO()
                    image.save(output, format='JPEG', optimize=True, quality=70)
                    output.seek(0)
                    photo = InMemoryUploadedFile(output, None, "%s.jpeg" % os.path.splitext(media.name)[0],
                                                 'image/jpeg', output.tell(), None)
                    PublicationImage.objects.create(publication=instance, image=photo)
            except IndexError:
                raise MediaNotSupported(u'No podemos procesar este tipo de archivo {file}.'.format(file=media.name))


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

        try:
            emitter = Profile.objects.get(user_id=self.request.user.id)
            board_owner = Profile.objects.get(user_id=request.POST['board_owner'])
        except NodeProfile.DoesNotExist as e:
            form.add_error('board_owner', 'El perfil donde quieres publicar no existe.')
            return self.form_invalid(form=form)

        privacity = board_owner.is_visible(emitter)

        if privacity and privacity != 'all':
            return HttpResponseForbidden()

        if form.is_valid():
            try:
                publication = form.save(commit=False)
                parent = publication.parent

                if parent:
                    parent_owner = parent.author_id
                    if RelationShipProfile.objects.is_blocked(to_profile=emitter.profile,
                                                              from_profile=parent.author.profile):
                        form.add_error('board_owner', 'El autor de la publicación te ha bloqueado.')
                        return self.form_invalid(form=form)

                publication.author_id = emitter.user_id
                publication.board_owner_id = board_owner.user_id

                publication.parse_content()  # parse publication content
                publication.parse_mentions()  # add mentions
                publication.add_hashtag()  # add hashtags
                publication.content = Emoji.replace(publication.content)  # Add emoji img

                media = request.FILES.getlist('image')

                try:
                    check_num_images(media)
                except MaxFilesReached:
                    form.add_error('content', 'El número máximo de imágenes que puedes subir es 5.')
                    return self.form_invalid(form=form)

                for file in media:
                    check_image_property(file)

                try:
                    exts = [magic.from_buffer(x.read(), mime=True).split('/') for x in media]
                except magic.MagicException as e:
                    form.add_error('content', 'No hemos podido procesar los archivos adjuntos.')
                    return self.form_invalid(form=form)

                have_video = False
                if any(word in 'gif video' for word in set([item for sublist in exts for item in sublist])):
                    have_video = True

                try:
                    with transaction.atomic(using="default"):
                        publication.save()  # Creamos publicacion
                        form.save_m2m()  # Saving tags
                        transaction.on_commit(
                            lambda: _optimize_publication_media(publication, media, exts))
                        transaction.on_commit(lambda: publication.send_notification(request, is_edited=False))
                        # enviamos a los seguidores
                        if publication.author_id == publication.board_owner_id:
                            transaction.on_commit(
                                lambda: send_to_stream.apply_async(args=[publication.author_id, publication.id],
                                                                   queue='low'))

                except (SizeIncorrect, MediaNotSupported, CantOpenMedia) as ex:
                    form.add_error('content', str(ex))
                    publication.delete()
                    return self.form_invalid(form=form)

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
                form.add_error('content', str(e))
                return self.form_invalid(form=form)

        return self.form_invalid(form=form)


publication_new_view = login_required(
    PublicationNewView.as_view(), login_url='/')


@login_required(login_url='/')
def publication_detail(request, publication_id):
    """
    Muestra el thread de una conversacion
    """
    user = request.user
    page = request.GET.get('page', 1)

    try:
        request_pub = Publication.objects \
            .select_related('author').get(id=publication_id, deleted=False)
    except ObjectDoesNotExist:
        raise Http404

    try:
        author = Profile.objects.get(user_id=request_pub.author_id)
        m = Profile.objects.get(user_id=user.id)
    except Profile.DoesNotExist:
        return redirect('user_profile:profile', username=request_pub.board_owner.username)

    privacity = author.is_visible(m)

    if privacity and privacity != 'all':
        return redirect('user_profile:profile', username=request_pub.board_owner.username)


    try:
        shared_publications = Publication.objects.filter(shared_publication__id=OuterRef('pk'),
                                                         deleted=False).order_by().values(
            'shared_publication__id')

        total_shared_publications = shared_publications.annotate(c=Count('*')).values('c')

        shared_for_me = shared_publications.annotate(have_shared=Count(Case(
            When(author_id=user.id, then=Value(1))
        ))).values('have_shared')

        publication = request_pub.get_descendants(include_self=True) \
            .annotate(likes=Count('user_give_me_like'),
                      hates=Count('user_give_me_hate'), have_like=Count(Case(
                When(user_give_me_like=user, then=Value(1)),
                output_field=IntegerField()
            )), have_hate=Count(Case(
                When(user_give_me_hate=user, then=Value(1)),
                output_field=IntegerField()
            ))) \
            .filter(deleted=False) \
            .prefetch_related('extra_content', 'images',
                              'videos', 'shared_publication__images',
                              'shared_publication__videos',
                              'shared_publication__extra_content',
                              'tags',
                              'shared_publication__author',
                              'shared_group_publication__images',
                              'shared_group_publication__author',
                              'shared_group_publication__videos',
                              'shared_group_publication__extra_content', ) \
            .select_related('author',
                            'board_owner', 'shared_publication',
                            'parent', 'shared_group_publication').annotate(
            total_shared=Subquery(total_shared_publications, output_field=IntegerField())).annotate(
            have_shared=Subquery(shared_for_me, output_field=IntegerField())).order_by('created')

    except Exception as e:
        logger.info(e)
        raise Exception('Error al cargar descendientes para la publicacion: {}'.format(request_pub))

    paginator = Paginator(publication, 10)

    try:
        publication = paginator.page(page)
    except PageNotAnInteger:
        publication = paginator.page(1)
    except EmptyPage:
        publication = paginator.page(paginator.num_pages)

    context = {
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
            publication = Publication.objects.prefetch_related('extra_content').select_related(
                'shared_publication').get(id=publication_id)
        except ObjectDoesNotExist:
            return HttpResponse(json.dumps(data),
                                content_type='application/json'
                                )
        logger.info('publication_author: {} publication_board_owner: {} request.user: {}'.format(
            publication.author.username, publication.board_owner.username, user.username))

        # Borramos publicacion
        if user.id == publication.author.id or user.id == publication.board_owner.id:
            try:
                with transaction.atomic(using="default"):
                    publication.deleted = True
                    publication.save(update_fields=['deleted'])
                    publication.get_descendants().update(deleted=True)
                    if publication.has_extra_content():
                        publication.extra_content.delete()
            except Exception as e:
                logger.info(e)
                return HttpResponse(json.dumps(data), content_type='application/json')
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
            author = Profile.objects.get(user_id=publication.author_id)
            m = Profile.objects.get(user_id=user.id)
        except Profile.DoesNotExist:
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

        if publication.user_give_me_like.filter(pk=user.pk).exists():  # Usuario en lista de likes
            in_like = True

        if publication.user_give_me_hate.filter(pk=user.pk).exists():  # Usuario en lista de hate
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
    if request.POST:
        user = request.user
        id_for_publication = request.POST['publication_id']  # Obtenemos el ID de la publicacion
        try:
            publication = Publication.objects.get(id=id_for_publication)  # Obtenemos la publicacion
        except ObjectDoesNotExist:
            data = json.dumps({'response': response, 'statuslike': statuslike})
            return HttpResponse(data, content_type='application/json')

        try:
            author = Profile.objects.get(user_id=publication.author_id)
            m = Profile.objects.get(user_id=user.id)
        except Profile.DoesNotExist:
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

        if publication.user_give_me_like.filter(pk=user.pk).exists():  # Usuario en lista de likes
            in_like = True

        if publication.user_give_me_hate.filter(pk=user.pk).exists():  # Usuario en lista de hate
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


@login_required()
def edit_publication(request):
    """
    Permite al creador de la publicacion
    editar el contenido de la publicacion
    """
    if request.method == 'POST':
        form = PublicationEdit(request.POST or None)

        if form.is_valid():
            content = form.cleaned_data['content']
            pk = form.cleaned_data['pk']
            user = request.user

            publication = get_object_or_404(Publication, id=pk)

            if publication.author.id != user.id:
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
def load_more_comments(request):
    """
    Carga respuestas de un comentario padre (carga comentarios hijos (nivel 1) de un comentario padre (nivel 0))
    o carga comentarios a respuestas (cargar comentarios descendientes (nivel > 1) de un comentario hijo (nivel 1))
    """
    if request.is_ajax():
        user = request.user
        pub_id = request.GET.get('pubid', None)  # publicacion padre
        page = request.GET.get('page', 1)  # Ultima publicacion add

        try:
            publication = Publication.objects.select_related('board_owner').get(id=pub_id)
        except ObjectDoesNotExist:
            raise Http404

        try:
            board_owner = Profile.objects.get(user_id=publication.board_owner_id)
            m = Profile.objects.get(user_id=user.id)
        except Profile.DoesNotExist:
            raise Http404

        privacity = board_owner.is_visible(m)

        if privacity and privacity != 'all':
            return HttpResponseForbidden()

        users_not_blocked_me = RelationShipProfile.objects.filter(
            to_profile=user.profile, type=BLOCK).values('from_profile_id')

        publications = publication.get_descendants() \
            .filter(
            ~Q(author__profile__in=users_not_blocked_me)
            & Q(deleted=False)).order_by('created')

        shared_publications = Publication.objects.filter(shared_publication__id=OuterRef('pk'),
                                                         deleted=False).order_by().values(
            'shared_publication__id')

        total_shared_publications = shared_publications.annotate(c=Count('*')).values('c')

        shared_for_me = shared_publications.annotate(have_shared=Count(Case(
            When(author_id=user.id, then=Value(1))
        ))).values('have_shared')

        publications = publications.annotate(likes=Count('user_give_me_like'),
                                             hates=Count('user_give_me_hate'), have_like=Count(Case(
                When(user_give_me_like=user, then=Value(1)),
                output_field=IntegerField()
            )), have_hate=Count(Case(
                When(user_give_me_hate=user, then=Value(1)),
                output_field=IntegerField()
            ))).prefetch_related('extra_content', 'images',
                                 'videos',
                                 'tags') \
            .select_related('author',
                            'board_owner',
                            'parent').annotate(
            total_shared=Subquery(total_shared_publications, output_field=IntegerField())).annotate(
            have_shared=Subquery(shared_for_me, output_field=IntegerField()))

        paginator = Paginator(publications, 10)

        try:
            publications = paginator.page(page)
        except PageNotAnInteger:
            publications = paginator.page(1)
        except EmptyPage:
            publications = paginator.page(paginator.num_pages)

        context = {
            'pub_id': pub_id,
            'publications': publications,
            'user_profile': publication.board_owner
        }
        return render(request, 'account/ajax_load_replies.html', context=context)

    return HttpResponseForbidden()


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
        user = request.user
        form = SharedPublicationForm(request.POST or None)
        print(request.POST)
        if form.is_valid():
            obj_pub = form.cleaned_data['pk']
            try:
                pub_to_add = Publication.objects.get(pk=obj_pub)
            except ObjectDoesNotExist:
                response = False
                return HttpResponse(json.dumps(response), content_type='application/json')

            try:
                author = Profile.objects.get(user_id=pub_to_add.author_id)
                m = Profile.objects.get(user_id=user.id)
            except Profile.DoesNotExist:
                return HttpResponse(json.dumps(response), content_type='application/json')

            privacity = author.is_visible(m)

            if privacity and privacity != 'all':
                return HttpResponse(json.dumps(response), content_type='application/json')

            shared = Publication.objects.filter(shared_publication_id=obj_pub, author_id=user.id,
                                                deleted=False).exists()

            if not shared:
                pub = form.save(commit=False)
                pub.parse_content()  # parse publication content
                pub.add_hashtag()
                pub.parse_mentions()  # add mentions
                pub.content = Emoji.replace(pub.content)

                pub.content = '<i class="material-icons blue1e88e5">format_quote</i> Ha compartido de <a ' \
                              'href="/profile/%s">@%s</a><br>%s' % (
                                  pub_to_add.author.username, pub_to_add.author.username, pub.content)

                pub.shared_publication_id = pub_to_add.id
                pub.author = user
                pub.board_owner = user
                pub.event_type = 6
                try:
                    with transaction.atomic(using="default"):
                        pub.save()
                        transaction.on_commit(lambda: pub.send_notification(request))
                    response = True
                except IntegrityError as e:
                    logger.info(e)
                logger.info('Compartido el comentario %d' % pub_to_add.id)

    return HttpResponse(json.dumps(response), content_type='application/json')


class RemoveSharedPublication(View):
    model = Publication

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(RemoveSharedPublication, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        pk = request.POST.get('pk', None)
        user = request.user

        try:
            pub_to_delete = Publication.objects.get(shared_publication_id=pk, author_id=user.id, deleted=False)
        except ObjectDoesNotExist:
            raise Http404

        id_to_delete = pub_to_delete.id

        try:
            pub_to_delete.deleted = True
            pub_to_delete.save(update_fields=['deleted'])
        except IntegrityError:
            data = {
                'response': False
            }
            return JsonResponse(data)

        data = {
            'response': True,
            'id_to_delete': id_to_delete
        }

        return JsonResponse(data)


def publication_filter_by_time(request):
    user = request.user
    if request.method == "POST":
        json_data = json.loads(request.body.decode('utf-8'))
        try:
            try:
                board_owner_id = int(json_data['board_owner'])
            except ValueError:
                return HttpResponse(json.dumps("No se encuentra el perfil seleccionado"),
                                    content_type='application/json')
        except KeyError:
            return HttpResponse(json.dumps("No se encuentra el perfil seleccionado"), content_type='application/json')

        try:
            owner = Profile.objects.get(user_id=board_owner_id)
            emitter = Profile.objects.get(user_id=user.id)
        except Profile.DoesNotExist:
            return HttpResponse(json.dumps("No puedes ver este perfil"), content_type='application/json')

        privacity = owner.is_visible(emitter)

        if privacity and privacity != 'all':
            return HttpResponse(json.dumps("No puedes ver este perfil"), content_type='application/json')

        root_nodes = cache_tree_children(
            Publication.objects.filter(board_owner_id=board_owner_id, deleted=False, level__lte=0).select_related(
                'author')[:5])
        dicts = []
        """
        for n in root_nodes:
            dicts.append(recursive_node_to_dict(n))
        """
        [dicts.append({
            'id': c.id,
            'content': c.content,
            'author__username': c.author.username,
            'created': naturaltime(c.created),
            'author__avatar': avatar_url(c.author)
        }) for c in root_nodes]
        return HttpResponse(json.dumps(dicts), content_type='application/json')
    return HttpResponse(json.dumps("Only POST METHOD"), content_type='application/json')


def publication_filter_by_like(request):
    user = request.user
    if request.method == "POST":
        json_data = json.loads(request.body.decode('utf-8'))
        try:
            try:
                board_owner_id = int(json_data['board_owner'])
            except ValueError:
                return HttpResponse(json.dumps("No se encuentra el perfil seleccionado"),
                                    content_type='application/json')
        except KeyError:
            return HttpResponse(json.dumps("No se encuentra el perfil seleccionado"), content_type='application/json')

        try:
            owner = Profile.objects.get(user_id=board_owner_id)
            emitter = Profile.objects.get(user_id=user.id)
        except Profile.DoesNotExist:
            return HttpResponse(json.dumps("No puedes ver este perfil"), content_type='application/json')

        privacity = owner.is_visible(emitter)

        if privacity and privacity != 'all':
            return HttpResponse(json.dumps("No puedes ver este perfil"), content_type='application/json')

        root_nodes = cache_tree_children(Publication.objects.annotate(likes=Count('user_give_me_like')) \
                                         .filter(board_owner_id=board_owner_id, deleted=False, level__lte=0).order_by(
            '-likes').select_related('author')[:5])

        dicts = []
        [dicts.append({
            'id': c.id,
            'content': c.content,
            'author__username': c.author.username,
            'created': naturaltime(c.created),
            'author__avatar': avatar_url(c.author),
            'likes': intword(c.likes)
        }) for c in root_nodes]
        """
        for n in root_nodes:
            dicts.append(recursive_node_to_dict(n))
        """
        return HttpResponse(json.dumps(dicts, indent=2), content_type='application/json')
    return HttpResponse(json.dumps("Only POST METHOD"), content_type='application/json')


def publication_filter_by_relevance(request):
    user = request.user
    if request.method == "POST":
        json_data = json.loads(request.body.decode('utf-8'))
        try:
            try:
                board_owner_id = int(json_data['board_owner'])
            except ValueError:
                return HttpResponse(json.dumps("No se encuentra el perfil seleccionado"),
                                    content_type='application/json')
        except KeyError:
            return HttpResponse(json.dumps("No se encuentra el perfil seleccionado"), content_type='application/json')

        try:
            owner = Profile.objects.get(user_id=board_owner_id)
            emitter = Profile.objects.get(user_id=user.id)
        except Profile.DoesNotExist:
            return HttpResponse(json.dumps("No puedes ver este perfil"), content_type='application/json')

        privacity = owner.is_visible(emitter)

        if privacity and privacity != 'all':
            return HttpResponse(json.dumps("No puedes ver este perfil"), content_type='application/json')

        root_nodes = cache_tree_children(Publication.objects.annotate(likes=Count('user_give_me_like')) \
                                         .filter(board_owner_id=board_owner_id, deleted=False, level__lte=0).order_by(
            '-likes', '-created').select_related('author')[:5])

        dicts = []
        [dicts.append({
            'id': c.id,
            'content': c.content,
            'author__username': c.author.username,
            'created': naturaltime(c.created),
            'author__avatar': avatar_url(c.author),
            'likes': intword(c.likes)
        }) for c in root_nodes]
        """
        for n in root_nodes:
            dicts.append(recursive_node_to_dict(n))
        """
        return HttpResponse(json.dumps(dicts, indent=2), content_type='application/json')
    return HttpResponse(json.dumps("Only POST METHOD"), content_type='application/json')
