import json
import logging
import os
import uuid
import PIL.Image as pil
from django.utils.six import BytesIO

from allauth.account.views import PasswordChangeView, EmailView
from dal import autocomplete
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from el_pagination.decorators import page_template
from el_pagination.views import AjaxListView
from django.http import JsonResponse
from django.core import serializers
from haystack.generic_views import SearchView
from haystack.query import SearchQuerySet
from notifications.models import Notification
from notifications.signals import notify
from photologue.models import Photo
from publications.forms import PublicationForm, ReplyPublicationForm, PublicationEdit, SharedPublicationForm
from publications.models import Publication, PublicationImage, PublicationVideo
from user_groups.forms import FormUserGroup
from user_profile.forms import AdvancedSearchForm
from user_profile.forms import ProfileForm, UserForm, \
    SearchForm, PrivacityForm, DeactivateUserForm, ThemesForm
from user_profile.models import NodeProfile, TagProfile, Request
from publications.utils import get_author_avatar
from neomodel import db
from django.db import transaction
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings
from mailer.mailer import Mailer
from .tasks import send_email
from django.db.models import Prefetch
from django.db.models import Count


@login_required(login_url='/')
@page_template("account/follow_entries.html", key='follow_entries')
def profile_view(request, username,
                 template="account/profile.html",
                 extra_context=None):
    """
    Vista principal del perfil de usuario.
    :param request:
    :param username => Username del perfil:
    :param template => Template por defecto que muestra el perfil:
    :param extra_context => Para paginacion :
    """
    user = request.user
    user_profile = get_object_or_404(get_user_model(),
                                     username__iexact=username)

    n = NodeProfile.nodes.get(user_id=user_profile.id)
    m = NodeProfile.nodes.get(user_id=user.id)

    context = {}
    # Privacidad del usuario
    privacity = n.is_visible(m)

    # Para escribir mensajes en mi propio perfil.
    group_initial = {'owner': user.pk}
    context['user_profile'] = user_profile
    context['node_profile'] = n
    context['privacity'] = privacity
    context['groupForm'] = FormUserGroup(initial=group_initial)

    # Cuando no tenemos permisos suficientes para ver nada del perfil
    if privacity == "nothing":
        template = "account/privacity/private_profile.html"
        return render(request, template, context)
    elif n.bloq.is_connected(m):
        template = "account/privacity/block_profile.html"
        return render(request, template, context)

    # Recuperamos requests para el perfil y si el perfil es gustado.
    if user.username != username:
        try:
            liked = m.has_like(to_like=user_profile.id)
        except Exception:
            liked = False
    else:
        liked = False

    # Recuperamos el numero de seguidores
    try:
        num_followers = n.count_followers()
    except Exception:
        num_followers = 0

    # Recuperamos el numero de seguidos y la lista de seguidos
    try:
        num_follows = n.count_follows()
    except Exception:
        num_follows = 0

    # Comprobamos si el perfil esta bloqueado
    isBlocked = False
    if user.username != username:
        try:
            isBlocked = m.bloq.is_connected(n)
        except Exception:
            pass

    # Comprobamos si el perfil es seguidor
    isFollower = False
    if user.username != username:
        try:
            isFollower = n.follow.is_connected(m)
        except Exception:
            pass
    # Comprobamos si el perfil es seguido
    isFollow = False
    if user.username != username:
        try:
            isFollow = m.follow.is_connected(n)
        except Exception:
            pass
    # Recuperamos el numero de contenido multimedia que tiene el perfil
    try:
        if user.username == username:
            multimedia_count = n.get_total_num_multimedia()
        else:
            multimedia_count = n.get_num_multimedia()
    except ObjectDoesNotExist:
        multimedia_count = 0
    # Comprobamos si existe una peticion de seguimiento
    try:
        friend_request = Request.objects.get_follow_request(from_profile=user.id, to_profile=user_profile.id)
    except ObjectDoesNotExist:
        friend_request = None

    context['liked'] = liked
    context['n_likes'] = n.count_likes()
    context['followers'] = num_followers
    context['following'] = num_follows
    context['isBlocked'] = isBlocked
    context['isFollower'] = isFollower
    context['isFriend'] = isFollow
    context['multimedia_count'] = multimedia_count
    context['existFollowRequest'] = True if friend_request else False

    if privacity == "followers" or privacity == "both":
        template = "account/privacity/need_confirmation_profile.html"
        return render(request, template, context)

    context['reply_publication_form'] = ReplyPublicationForm()
    context['publicationForm'] = PublicationForm()
    context['publication_edit'] = PublicationEdit()
    context['publication_shared'] = SharedPublicationForm()

    # cargar lista comentarios
    try:
        # if user_profile.username == username:
        # Get user_profile publications LIMIT 20
        publications = Publication.objects.filter(board_owner_id=user_profile.id,
                            level__lte=0, deleted=False) \
                            .prefetch_related('extra_content', 'images',
                                'videos', 'shared_publication__images',
                                'tags',
                                'shared_photo_publication__images',
                                'shared_publication__author',
                                'shared_photo_publication__p_author',
                                'shared_photo_publication__videos',
                                'shared_photo_publication__publication_photo_extra_content',
                                'shared_publication__videos', 'shared_publication__extra_content', 'user_give_me_like', 'user_give_me_hate') \
                            .select_related('author',
                            'board_owner', 'shared_publication', 'parent', 'shared_photo_publication')[:20]

        # Obtenemos los ids de las publicaciones del skyline
        # Despues recuperamos aquellas publicaciones que han sido compartidas
        shared_id = publications.values_list('id', flat=True)
        pubs_shared = Publication.objects.filter(shared_publication__id__in=shared_id, deleted=False).values('shared_publication__id')\
                .order_by('shared_publication__id')\
                .annotate(total=Count('shared_publication__id'))

        pubs_shared_with_me = Publication.objects.filter(shared_publication__id__in=shared_id, author__id=user.id, deleted=False).values('author__id', 'shared_publication__id')


        """
        publications = [node.get_descendants(include_self=True).filter(deleted=False, level__lte=1) \
                .prefetch_related('images', 'videos', 'user_give_me_hate', 'user_give_me_like', 'extra_content') \
                .select_related('author', 'board_owner',
                            'shared_publication', 'parent', 'shared_photo_publication')[:10]
                            for node in
                            Publication.objects.filter(
                                board_owner_id=user_profile.id, deleted=False,
                                parent=None).only('id', 'level', 'tree_id', 'lft', 'rght')[:20]]
        """
    except ObjectDoesNotExist:
        publications = None


    # context['shares'] = shares
    # Contenido de las tres tabs
    context['pubs_shared_with_me'] = pubs_shared_with_me
    context['pubs_shared'] = pubs_shared
    context['publications'] = list(publications)
    context['component'] = 'react/publications.js'
    context['friends_top12'] = n.get_follows()

    if extra_context is not None:
        context.update(extra_context)

    return render(request, template, context)


@login_required(login_url='accounts/login')
def search(request, option=None):
    """
    View principal para realizar una busqueda en la web.
    :param request:
    :param option:
    :return resultados de la busqueda:

    Se añade una variable 'option' inicializada a None, para que por defecto
    busque las palabras en usuarios y publicaciones, pero que si tiene algún
    valor, haga la búsqueda únicamente por ese campo.
    """
    # para mostarar tambien el cuadro de busqueda en la pagina
    user = request.user
    searchForm = SearchForm(request.POST)
    info = request.method

    if request.method == 'GET' and option is None:
        '''
        if 'searchText' in request.session:
            request.POST = request.session['searchText']
            request.method = 'POST'
        '''
        # NOTE Modificado por adrian:
        # Si hay peticion GET => Se busca si antes hubo
        # un request.POST
        # Si hay peticion POST se actúa con normalidad
        return render(request, 'account/search.html',
                      {'showPerfilButtons': True,
                       'searchForm': searchForm,
                       'resultSearch': (),
                       'message': info})

    # if request.method == 'POST':
    else:
        if searchForm.is_valid:
            result_search = None
            result_messages = None
            result_media = None
            try:
                texto_to_search = request.POST['searchText']
                request.session['searchText'] = request.POST['searchText']
            except:
                texto_to_search = request.session['searchText']
            # hacer busqueda si hay texto para buscar, mediante consulta a la
            # base de datos y pasar el resultado
            searchForm = SearchForm(initial={'searchText': texto_to_search})
            if texto_to_search:
                words = texto_to_search.split()

                # Búsqueda predeterminada o de cuentas.
                if option is None or option == 'accounts':
                    if len(words) == 1:
                        result_search = User.objects.filter(Q(first_name__icontains=texto_to_search) |
                                                            Q(last_name__icontains=texto_to_search) |
                                                            Q(username__icontains=texto_to_search),
                                                            Q(is_active=True),
                                                            ~Q(username=request.user.username))

                    elif len(words) == 2:
                        result_search = User.objects.filter(Q(first_name__icontains=words[0]),
                                                            Q(last_name__icontains=words[1]),
                                                            Q(is_active=True),
                                                            ~Q(username=request.user.username))
                    else:
                        result_search = User.objects.filter(Q(first_name__icontains=words[0]),
                                                            Q(last_name__icontains=words[1] + ' ' + words[2]),
                                                            Q(is_active=True))
                # usamos la expresion regular para descartar las imagenes de los comentarios.
                # Búsqueda predeterminada o de publicaciones.
                # IDEA Mejorar consulta a bbdd (pasando lista words)
                # en lugar de recorrer la lista y buscar cada palabra
                if option is None or option == 'publications':
                    for w in words:
                        result_messages = Publication.objects.filter(
                            Q(content__iregex=r"\b%s\b" % w) & ~Q(content__iregex=r'<img[^>]+src="([^">]+)"') |
                            Q(author__username__icontains=w) |
                            Q(author__first_name__icontains=w) |
                            Q(author__last_name__icontains=w), Q(author__is_active=True),
                            ~Q(author__username__icontains=request.user.username)).order_by('content').order_by(
                            'created').reverse()  # or .order_by('created').reverse()
                # GET MEDIA BY OWNER OR TAGS...
                if option == 'images':
                    if len(words) == 1:
                        result_media = Photo.objects.filter(Q(tags__name__in=words) | (
                            Q(owner__username__icontains=texto_to_search) & ~Q(owner__username=request.user.username)))
                    elif len(words) > 1:
                        for w in words:
                            pass
                return render(request, 'account/search.html', {'showPerfilButtons': True,
                                                               'resultSearch': result_search,
                                                               'searchForm': searchForm,
                                                               'resultMessages': result_messages,
                                                               'result_media': result_media,
                                                               'words': words,
                                                               'message': info, })


@login_required(login_url='/')
def advanced_view(request):
    """
    Búsqueda avanzada
    """
    user = request.user
    template_name = "account/search-avanzed.html"
    searchForm = SearchForm(request.POST)

    http_method = request.method

    if http_method == 'GET':
        form = AdvancedSearchForm()

    elif http_method == 'POST':
        form = AdvancedSearchForm(request.POST)
        if form.is_valid():
            clean_all_words = form.cleaned_data['all_words']
            clean_exactly = form.cleaned_data['word_or_exactly_word']
            clean_some = form.cleaned_data['some_words']
            clean_none = form.cleaned_data['none_words']
            clean_hashtag = form.cleaned_data['hashtags']
            clean_regex = form.cleaned_data['regex_string']

        if clean_all_words:
            import operator
            from functools import reduce
            word_list = [x.strip() for x in clean_all_words.split(',')]
            result_all_words = Publication.objects.filter(
                reduce(operator.and_, (Q(content__icontains=x) for x in word_list)))
            print(result_all_words)

        if clean_exactly:
            result_exactly = Publication.objects.filter(
                Q(content__iexact=clean_exactly) | Q(content__iexact=('\n'.join(clean_exactly))))
            print(result_exactly)

        if clean_some:
            result_some = Publication.objects.filter(content__icontains=clean_some)
            print(result_some)

        if clean_none:
            result_none = Publication.objects.filter(~Q(content__icontains=clean_none))
            print(result_none)

        if clean_hashtag:
            clean_hashtag = [x.strip() for x in clean_hashtag.split(',')]
            print(clean_hashtag)
            result_hashtag = Publication.objects.filter(tags__name__in=clean_hashtag)
            print(result_hashtag)

        if clean_regex:
            result_regex = Publication.objects.filter(content__iregex=clean_regex)
            print(result_regex)

    return render(request, template_name, {'form': form, })


@login_required(login_url='/')
def config_privacity(request):
    user = request.user
    try:
        user_profile = NodeProfile.nodes.get(user_id=user.id)
    except NodeProfile.DoesNotExist:
        raise Http404

    logging.info('>>>>> PETICION CONFIG - User: {}'.format(user.username))
    if request.POST:
        privacity_form = PrivacityForm(data=request.POST)
        if privacity_form.is_valid():
            try:
                user_profile.privacity = privacity_form.clean_privacity()
                user_profile.save()
                print(user_profile.privacity)
            except Exception:
                logging.info('>>>> PETICION CONFIG - User: {} - ERROR'.format(user.username))
            logging.info('>>>> PETICION CONFIG - User: {} - CAMBIOS GUARDADOS CORRECTAMENTE'.format(user.username))
        return HttpResponseRedirect('/config/privacity')
    else:
        privacity_form = PrivacityForm(initial={'privacity': user_profile.privacity})

    props = {
        'users': [
            {
                'username': user.username,
                'id': user.id
            }
        ]
    }

    return render(request, 'account/cf-privacity.html',
                  {'showPerfilButtons': True,
                   'privacity_form': privacity_form,
                   'props': props,
                   'component': 'leaderboard.js'
                   })


@login_required(login_url='/')
def config_profile(request):
    user_profile = request.user
    node = NodeProfile.nodes.get(user_id=user_profile.id)
    logging.info('>>>>>>>  PETICION CONFIG')
    if request.POST:
        # formulario enviado
        logging.info('>>>>>>>  paso 1' + str(request.FILES))
        user_form = UserForm(data=request.POST, instance=request.user)
        perfil_form = ProfileForm(request.POST, request.FILES)

        logging.info('>>>>>>>  paso 1.1')
        if user_form.is_valid() and perfil_form.is_valid():
            # formulario validado correctamente
            logging.info('>>>>>>  save')
            try:
                with transaction.atomic(using='default'):
                    with db.transaction:
                        node.first_name = user_form.cleaned_data['first_name']
                        node.last_name = user_form.cleaned_data['last_name']
                        node.status = perfil_form.clean_status()
                        data = perfil_form.clean_backImage()
                        if data:
                            file_id = str(uuid.uuid4())  # random filename
                            filename, file_extension = os.path.splitext(data.name)  # get extension
                            fs = FileSystemStorage()  # get filestorage
                            img = pil.open(data)
                            img.thumbnail((1500, 500), pil.ANTIALIAS)
                            thumb_io = BytesIO()
                            img.save(thumb_io, format=data.content_type.split('/')[-1].upper(), quality=95,
                                     optimize=True)
                            thumb_io.seek(0)
                            file = InMemoryUploadedFile(thumb_io,
                                                        None,
                                                        filename,
                                                        data.content_type,
                                                        thumb_io.tell(),
                                                        None)
                            filename = fs.save(file_id + file_extension, file)  # get filename
                            filename, file_extension = os.path.splitext(filename)  # only if save change "file_id"
                            node.back_image = filename  # assign filename to back_image node
                        node.save()
                        user_form.save()
            except Exception as e:
                logging.info(
                    "No se pudo guardar la configuracion del perfil de la cuenta: {}".format(user_profile.username))
            return HttpResponseRedirect('/config/profile')
    else:
        # formulario inicial
        user_form = UserForm(instance=request.user)
        perfil_form = ProfileForm(initial={'status': node.status})

    logging.Manager('>>>>>>>  paso x')
    context = {'showPerfilButtons': True,
               'user_profile': user_profile,
               'node_profile': node,
               'user_form': user_form, 'perfil_form': perfil_form,
               }
    return render(request, 'account/cf-profile.html', context)
    # return render_to_response('account/cf-profile.html',
    # {'showPerfilButtons':True,'searchForm':searchForm,
    # 'user_form':user_form}, context_instance=RequestContext(request))


@login_required(login_url='/')
def config_pincode(request):
    user = request.user
    user_profile = NodeProfile.nodes.get(user_id=user.id)
    initial = {'author': user.pk, 'board_owner': user.pk}
    pin = user_profile.uid

    context = {'showPerfilButtons': True,
               'pin': pin,
               }

    return render(request, 'account/cf-pincode.html', context)


@login_required(login_url='/')
def config_blocked(request):
    user = request.user
    n = NodeProfile.nodes.get(user_id=user.id)
    list_blocked = n.bloq.match()

    return render(request, 'account/cf-blocked.html', {'showPerfilButtons': True,
                                                       'blocked': list_blocked,
                                                       })


@login_required(login_url='accounts/login')
def add_friend_by_username_or_pin(request):
    """
    Funcion para añadir usuario por nombre de usuario y perfil
    """
    logging.info('ADD FRIEND BY USERNAME OR PIN')
    response = 'no_added_friend'
    friend = None
    data = {
        'response': response,
        'friend': friend
    }
    if request.method == 'POST':
        pin = str(request.POST.get('valor'))
        if len(pin) > 15:
            user_request = request.user

            try:
                user = NodeProfile.nodes.get(user_id=user_request.id)
            except NodeProfile.DoesNotExist:
                return HttpResponse(
                    json.dumps(json.dumps({'response': 'your_own_pin'}), content_type='application/javascript'))

            logging.info('Pin: {}'.format(pin))

            if str(user.uid).strip() == pin.strip():
                return HttpResponse(json.dumps({'response': 'your_own_pin'}), content_type='application/javascript')
            else:
                logging.info('personal_pin: {} pin: {}'.format(user.uid, pin))

            try:
                friend = NodeProfile.nodes.get(uid=pin)
            except ObjectDoesNotExist:
                data['response'] = 'no_match'
                return HttpResponse(json.dumps(data), content_type='application/javascript')

            if user.follow.is_connected(friend):
                data['response'] = 'its_your_friend'
                data['friend'] = friend.title
                return HttpResponse(json.dumps(data), content_type='application/javascript')

            # Me tienen bloqueado
            if friend.bloq.is_connected(user):
                data['response'] = 'user_blocked'
                data['friend'] = friend.title
                return HttpResponse(json.dumps(data), content_type='application/javascript')

            # Yo tengo bloqueado al perfil
            if user.bloq.is_connected(friend):
                data['response'] = 'blocked_profile'
                data['friend'] = friend.title
                return HttpResponse(json.dumps(data), content_type='application/javascript')

            # Comprobamos si el usuario necesita peticion de amistad
            no_need_petition = friend.privacity == NodeProfile.ALL
            if no_need_petition:
                user.follow.connect(friend)
                data['response'] = 'added_friend'
                data['friend_username'] = friend.title
                data['friend_avatar'] = get_author_avatar(friend.user_id)
                data['friend_first_name'] = User.objects.get(id=friend.user_id).first_name
                data['friend_last_name'] = User.objects.get(id=friend.user_id).last_name
                return HttpResponse(json.dumps(data), content_type='application/javascript')

            # enviamos peticion de amistad
            try:
                friend_request = Request.objects.get_follow_request(from_profile=user.user_id,
                                                                    to_profile=friend.user_id)
            except ObjectDoesNotExist:
                friend_request = None

            if not friend_request:
                # Eliminamos posibles notificaciones residuales
                Notification.objects.filter(actor_object_id=user_request.pk,
                                            recipient=friend.user,
                                            level='friendrequest').delete()
                # Enviamos la notificacion
                notification = notify.send(user_request, actor=User.objects.get(pk=user_request.pk).username,
                                           recipient=friend.user,
                                           verb=u'quiere seguirte.', level='friendrequest')
                # Enlazamos notificacion con peticion de amistad
                try:
                    created = Request.objects.add_follow_request(user.user_id, friend.user_id, notification[0][1])
                    response = 'new_petition'
                except ObjectDoesNotExist:
                    response = "no_added_friend"

        else:  # tipo == username
            user_request = request.user
            username = pin

            try:
                user = NodeProfile.nodes.get(user_id=user_request.id)
            except NodeProfile.DoesNotExist:
                return HttpResponse(
                    json.dumps(json.dumps({'response': 'your_own_pin'}), content_type='application/javascript'))

            if user.title == username:
                data['response'] = 'your_own_username'
                return HttpResponse(json.dumps(data), content_type='application/javascript')

            try:
                friend = NodeProfile.nodes.get(title=username)
            except ObjectDoesNotExist:
                data['response'] = 'no_match'
                return HttpResponse(json.dumps(data), content_type='application/javascript')

            if user.follow.is_connected(friend):  # if user.is_friend(friend):
                data['response'] = 'its_your_friend'
                data['friend'] = friend.title
                return HttpResponse(json.dumps(data), content_type='application/javascript')

            # Me tienen bloqueado
            if friend.bloq.is_connected(user):
                data['response'] = 'user_blocked'
                data['friend'] = friend.title
                return HttpResponse(json.dumps(data), content_type='application/javascript')

            # Yo tengo bloqueado al perfil
            if user.bloq.is_connected(friend):
                data['response'] = 'blocked_profile'
                data['friend'] = friend.title
                return HttpResponse(json.dumps(data), content_type='application/javascript')

            # Comprobamos si el usuario necesita peticion de amistad
            no_need_petition = friend.privacity == NodeProfile.ALL
            if no_need_petition:
                user.follow.connect(friend)
                data['response'] = 'added_friend'
                data['friend_username'] = friend.title
                data['friend_avatar'] = get_author_avatar(friend.user_id)
                data['friend_first_name'] = User.objects.get(id=friend.user_id).first_name
                data['friend_last_name'] = User.objects.get(id=friend.user_id).last_name
                return HttpResponse(json.dumps(data), content_type='application/javascript')

            # enviamos peticion de amistad
            try:
                friend_request = Request.objects.get_follow_request(from_profile=user.user_id,
                                                                    to_profile=friend.user_id)
                response = 'in_progress'
            except ObjectDoesNotExist:
                friend_request = None

            if not friend_request:
                # Eliminamos posibles notificaciones residuales
                Notification.objects.filter(actor_object_id=user_request.pk,
                                            recipient=friend.user,
                                            level='friendrequest').delete()
                # Enviamos nueva notificacion
                notification = notify.send(user_request, actor=User.objects.get(pk=user_request.pk).username,
                                           recipient=friend.user,
                                           verb=u'quiere seguirte.', level='friendrequest')
                # Enlazamos notificacion y peticion de amistad
                try:
                    created = Request.objects.add_follow_request(user.user_id, friend.user_id, notification[0][1])
                    response = 'new_petition'
                except ObjectDoesNotExist:
                    response = "no_added_friend"

    data['response'] = response
    data['friend_username'] = friend.user.username
    data['friend_avatar'] = get_author_avatar(friend.user_id)
    data['friend_first_name'] = User.objects.get(id=friend.user_id).first_name
    data['friend_last_name'] = User.objects.get(id=friend.user_id).last_name
    return HttpResponse(json.dumps(data), content_type='application/javascript')


@login_required(login_url='/')
def like_profile(request):
    """
    Funcion para dar like al perfil
    """
    response = "null"
    if request.method == 'POST':
        user = request.user
        slug = int(request.POST.get('slug', None))

        actual_profile = get_object_or_404(User,
                                           id=slug)
        n = NodeProfile.nodes.get(user_id=user.id)
        m = NodeProfile.nodes.get(user_id=slug)

        if n.like.is_connected(m):
            n.like.disconnect(NodeProfile.nodes.get(user_id=slug))
            rel = n.follow.relationship(m)
            if rel:
                rel.weight = rel.weight - 10
                rel.save()
            response = "nolike"
        else:
            try:
                with transaction.atomic(using="default"):
                    with db.transaction:
                        n.like.connect(NodeProfile.nodes.get(user_id=slug))
                        rel = n.follow.relationship(m)
                        if rel:
                            rel.weight = rel.weight + 10
                            rel.save()
                        notify.send(user, actor=User.objects.get(pk=user.pk).username,
                                           recipient=actual_profile,
                                           verb=u'¡<a href="/profile/%s">@%s</a> te ha dado me gusta a tu perfil!.' % (user.username, user.username), level='like_profile')
                response = "like"
            except Exception as e:
                pass

            # Enviar email...
            send_email.delay('Skyfolk - %s te ha dado un like.' % user.username, [actual_profile.email],
                    {'to_user': actual_profile.username,'from_user': user.username}
                    , 'emails/like_profile.html')

        logging.info('%s da like a %s' % (user.username, actual_profile.username))
        logging.info('Nueva afinidad emitter: {} receiver: {}'.format(user.username, actual_profile.username))
        logging.info("Response: " + response)

    return HttpResponse(json.dumps(response), content_type='application/javascript')


# Request follow
@login_required(login_url='accounts/login')
def request_friend(request):
    """
    Funcion para solicitudes de amistad
    """
    logging.info('>>>>>>> peticion amistad ')
    response = "null"
    if request.method == 'POST':
        user = request.user
        slug = int(request.POST.get('slug', None))

        n = NodeProfile.nodes.get(user_id=user.id)
        m = NodeProfile.nodes.get(user_id=slug)

        # El perfil me ha bloqueado

        if m.bloq.is_connected(n):
            response = "user_blocked"
            return HttpResponse(json.dumps(response), content_type='application/javascript')

        try:
            user_friend = n.follow.is_connected(m)  # Comprobamos si YO ya sigo al perfil deseado.
        except Exception:
            user_friend = None

        if user_friend:
            response = "isfriend"
        else:
            # Comprobamos si el perfil necesita peticion de amistad
            no_need_petition = m.privacity == NodeProfile.ALL
            if no_need_petition:
                n.follow.connect(m)
                response = "added_friend"
                # enviamos notificacion informando del evento

                recipient = User.objects.get(id=m.user_id)

                notify.send(user, actor=n.title,
                            recipient=recipient,
                            verb=u'¡ahora te sigue <a href="/profile/%s">%s</a>!.' % (n.title, n.title),
                            level='new_follow')

                # enviamos mail
                send_email.delay('Skyfolk - %s ahora te sigue.' % user.username, [recipient.email],
                    {'to_user': recipient.username,'from_user': user.username}
                    , 'emails/new_follow.html')

                return HttpResponse(json.dumps(response), content_type='application/javascript')
            response = "inprogress"

            try:
                friend_request = Request.objects.get_follow_request(from_profile=n.user_id, to_profile=m.user_id)
            except ObjectDoesNotExist:
                friend_request = None

            if not friend_request:
                # Eliminamos posibles notificaciones residuales
                Notification.objects.filter(actor_object_id=n.user_id,
                                            recipient=m.user_id,
                                            level='friendrequest').delete()

                recipient = User.objects.get(id=m.user_id)
                # Creamos y enviamos la nueva notificacion
                notification = notify.send(user, actor=n.title,
                                           recipient=recipient,
                                           verb=u'quiere seguirte.', level='friendrequest')

                # Enlazamos notificacion con peticion de amistad
                try:
                    created = Request.objects.add_follow_request(n.user_id,
                                                                 m.user_id,
                                                                 notification[0][1])
                    send_email.delay('Skyfolk - %s quiere seguirte.' % user.username, [recipient.email],
                        {'to_user': recipient.username,'from_user': user.username} ,
                        'emails/follow_request.html')

                except ObjectDoesNotExist:
                    response = "no_added_friend"

        logging.info(response)

    return HttpResponse(json.dumps(response), content_type='application/javascript')


# Responde request follow
@login_required(login_url='/')
def respond_friend_request(request):
    """
    Funcion para respuesta a solicitud de amistad
    """
    response = "null"
    if request.method == 'POST':
        user = request.user
        profile_user_id = int(request.POST.get('slug', None))
        request_status = request.POST.get('status', None)

        try:
            n = NodeProfile.nodes.get(user_id=profile_user_id)
            m = NodeProfile.nodes.get(user_id=user.id)
        except NodeProfile.DoesNotExist:
            return HttpResponse(json.dumps(response), content_type='application/javascript')

        if request_status == 'accept':
            n.follow.connect(m)
            logging.info('user.profile: {} emitter_profile: {}'.format(m.title, n.title))

            # enviamos notificacion informando del evento
            recipient = User.objects.get(id=profile_user_id)
            notify.send(user, actor=m.title,
                        recipient=recipient,
                        verb=u'¡ahora sigues a <a href="/profile/%s">%s</a>!.' % (m.title, m.title),
                        evel='new_follow')

            send_email.delay('Skyfolk - %s ha aceptado tu solicitud.' % user.username, [recipient.email],
                        {'to_user': recipient.username,'from_user': user.username} ,
                        'emails/new_follow_added.html')

            response = "added_friend"

        elif request_status == 'rejected':
            response = "rejected"
        else:
            response = "rejected"

        Request.objects.remove_received_follow_request(from_profile=n.user_id, to_profile=m.user_id)

    return HttpResponse(json.dumps(response), content_type='application/javascript')


# Elimina relación entre dos usuarios
@login_required(login_url='/')
def remove_relationship(request):
    """
    Elimina relacion seguidor/seguido
    """
    response = None
    user = request.user
    slug = int(request.POST.get('slug', None))

    if request.method == 'POST':
        try:
            profile_user = NodeProfile.nodes.get(user_id=slug)
            me = NodeProfile.nodes.get(user_id=user.id)
        except NodeProfile.DoesNotExist:
            return HttpResponse(json.dumps(response), content_type='application/javascript')

        try:
            me.follow.disconnect(profile_user)  # Comprobamos si YO ya sigo al perfil deseado.
            response = True
        except Exception:
            response = None

    return HttpResponse(json.dumps(response), content_type='application/javascript')


@login_required(login_url='/')
def remove_blocked(request):
    """
    Elimina relacion de bloqueo
    """
    response = None
    user = request.user
    slug = int(request.POST.get('slug', None))
    try:
        m = NodeProfile.nodes.get(user_id=user.id)
        n = NodeProfile.nodes.get(user_id=slug)
    except Exception:
        return HttpResponse(json.dumps(response), content_type='application/javascript')

    logging.info('%s ya no bloquea a %s' % (m.title, n.title))

    if request.method == 'POST':
        try:
            m.bloq.disconnect(n)
            response = True
        except Exception:
            response = False

    return HttpResponse(json.dumps(response), content_type='application/javascript')


# Elimina la peticion existente para seguir a un perfil
@login_required(login_url='/')
def remove_request_follow(request):
    """
    Elimina relacion de seguidos
    """
    response = False
    user = request.user
    slug = int(request.POST.get('slug', None))
    status = request.POST.get('status', None)

    logging.info('REMOVE REQUEST FOLLOW: u1: {} - u2: {}'.format(user.id, slug))
    if request.method == 'POST':
        if status == 'cancel':
            response = Request.objects.remove_received_follow_request(from_profile=user.id, to_profile=slug)
        else:
            response = False
        logging.info('Response -> ' + str(response))
    return HttpResponse(json.dumps(response), content_type='application/javascript')


# Load followers
@login_required(login_url='/')
def load_followers(request):
    """
    Funcion para cargar seguidores
    :return lista de seguidores:
    """
    logging.info('>>>>>> PETICION AJAX, CARGAR MAS AMIGOS')

    try:
        m = NodeProfile.nodes.get(user_id=request.user.id)
    except NodeProfile.DoesNotExist:
        friends_next = None
        return HttpResponse(json.dumps(list(friends_next)), content_type='application/json')

    friendslist = m.get_followers()

    if friendslist is None:
        friends_next = None
    else:
        # friendslist = json.loads(friendslist)
        if request.method == 'POST':
            slug = request.POST.get('slug', None)
            logging.info('>>>>>>> SLUG: ' + slug)
            n = int(slug) * 2
            # devolvera None si esta fuera de rango?
            friends_next = friendslist[n - 2:n]
            logging.info('>>>>>>> LISTA: ')
            logging.info(friends_next)
        else:
            friends_next = None
    return HttpResponse(json.dumps(list(friends_next)), content_type='application/json')


class FollowersListView(AjaxListView):
    """
    Lista de seguidores del usuario
    """
    context_object_name = "friends_top4"
    template_name = "account/relations.html"
    page_template = "account/relations_page.html"

    def get_queryset(self):

        try:
            n = NodeProfile.nodes.get(title__iexact=self.kwargs['username'])
        except Exception:
            raise Http404

        return n.get_followers()

    def get_context_data(self, **kwargs):
        context = super(FollowersListView, self).get_context_data(**kwargs)
        user = self.request.user
        context['url_name'] = "followers"
        return context


followers = login_required(FollowersListView.as_view())


class FollowingListView(AjaxListView):
    """
    Lista de seguidos del usuario
    """
    context_object_name = "friends_top4"
    template_name = "account/relations.html"
    page_template = "account/relations_page.html"

    def get_queryset(self):
        try:
            n = NodeProfile.nodes.get(title__iexact=self.kwargs['username'])
        except Exception:
            raise Http404

        return n.get_follows()

    def get_context_data(self, **kwargs):
        context = super(FollowingListView, self).get_context_data(**kwargs)
        user = self.request.user
        context['url_name'] = "following"
        return context


following = login_required(FollowingListView.as_view())


# Load follows
@login_required(login_url='/')
def load_follows(request):
    """
    Funcion para cargar mas seguidos
    :return lista de seguidos:
    """
    logging.info('>>>>>> PETICION AJAX, CARGAR MAS AMIGOS')
    try:
        m = NodeProfile.nodes.get(user_id=request.user.id)
    except NodeProfile.DoesNotExist:
        friends_next = None
        return HttpResponse(json.dumps(list(friends_next)), content_type='application/json')

    friendslist = m.get_follows()

    if friendslist is None:
        friends_next = None
    else:
        # friendslist = json.loads(friendslist)
        if request.method == 'POST':
            slug = request.POST.get('slug', None)
            logging.info('>>>>>>> SLUG: ' + slug)
            n = int(slug) * 4
            # devolvera None si esta fuera de rango?
            friends_next = friendslist[n - 4:n]
            logging.info('>>>>>>> LISTA: ')
            logging.info(friends_next)
        else:
            friends_next = None
    return HttpResponse(json.dumps(list(friends_next)), content_type='application/json')


class PassWordChangeDone(TemplateView):
    template_name = 'account/confirmation_changepass.html'

    def get(self, request, *args, **kwargs):
        context = locals()
        user = self.request.user
        context['showPerfilButtons'] = True
        return render(request, self.template_name, context)


password_done = login_required(PassWordChangeDone.as_view())


# Modificacion del formulario para cambiar contraseña
class CustomPasswordChangeView(PasswordChangeView):
    success_url = reverse_lazy("user_profile:account_done_password")

    def get_context_data(self, **kwargs):
        ret = super(PasswordChangeView, self).get_context_data(**kwargs)
        # NOTE: For backwards compatibility
        ret['password_change_form'] = ret.get('form')
        user = self.request.user
        ret['showPerfilButtons'] = True
        # (end NOTE)
        return ret


custom_password_change = login_required(CustomPasswordChangeView.as_view())


# Modificacion del formulario para manejar los emails
class CustomEmailView(EmailView):
    success_url = reverse_lazy('user_profile:account_email')

    def get_context_data(self, **kwargs):
        ret = super(EmailView, self).get_context_data(**kwargs)
        # NOTE: For backwards compatibility
        user = self.request.user
        ret['add_email_form'] = ret.get('form')
        ret['showPerfilButtons'] = True
        # (end NOTE)
        return ret


custom_email = login_required(CustomEmailView.as_view())


@login_required(login_url='/')
def changepass_confirmation(request):
    return render(request, 'account/confirmation_changepass.html')


# Modificacion del template para desactivar una cuenta
class DeactivateAccount(FormView):
    template_name = 'account/cf-account_inactive.html'
    form_class = DeactivateUserForm
    success_url = reverse_lazy('account_logout')

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['form'] = self.form_class
        user = self.request.user
        self_initial = {'author': user.pk, 'board_owner': user.pk}

        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = self.get_form(self.form_class)
        user = request.user
        if user.is_authenticated():
            if form.is_valid():
                try:
                    node_profile = NodeProfile.nodes.get(user_id=user.id)
                except NodeProfile.DoesNotExist:
                    raise ObjectDoesNotExist

                try:
                    with transaction.atomic(using='default'):
                        with db.transaction:
                            is_active = not (form.clean_is_active())
                            user.is_active = is_active
                            node_profile.is_active = is_active
                            node_profile.save()
                            user.save()
                except Exception as e:
                    logging.info("La cuenta de: {} no se pudo desactivar".format(user.username))

                if user.is_active:
                    return self.form_valid(form=form, **kwargs)
                else:
                    return HttpResponseRedirect(self.success_url)
            else:
                return self.form_invalid(form=form, **kwargs)
        else:
            raise PermissionError

    def form_valid(self, form, **kwargs):
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return self.render_to_response(context)

    def form_invalid(self, form, **kwargs):
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return self.render_to_response(context)


custom_delete_account = login_required(DeactivateAccount.as_view())


@login_required(login_url='/')
def bloq_user(request):
    """
        Funcion para bloquear usuarios
    """
    user = request.user
    haslike = "noliked"
    status = "none"

    if request.method == 'POST':
        id_user = request.POST.get('id_user', None)

        if id_user == user.id:
            data = {'response': False, 'haslike': haslike}
            return HttpResponse(json.dumps(data), content_type='application/json')

        try:
            n = NodeProfile.nodes.get(user_id=id_user)
            m = NodeProfile.nodes.get(user_id=user.id)
        except NodeProfile.DoesNotExist:
            data = {'response': False, 'haslike': haslike}
            return HttpResponse(json.dumps(data), content_type='application/json')

        # Eliminar me gusta al perfil que se va a bloquear

        if m.like.is_connected(n):
            m.like.disconnect(n)
            haslike = "liked"

        # Ver si hay una peticion de "seguir" pendiente
        try:
            follow_request = Request.objects.get_follow_request(from_profile=m.user_id, to_profile=n.user_id)
        except ObjectDoesNotExist:
            follow_request = None

        if follow_request:
            Request.objects.remove_received_follow_request(from_profile=m.user_id, to_profile=n.user_id)
            status = "inprogress"

        # Ver si seguimos al perfil que vamos a bloquear

        if m.follow.is_connected(n):
            m.follow.disconnect(n)
            n.follow.disconnect(m)
            status = "isfollow"

        # Ver si hay una peticion de "seguir" pendiente (al perfil contrario)
        try:
            follow_request_reverse = Request.objects.get_follow_request(from_profile=n.user_id, to_profile=m.user_id)
        except ObjectDoesNotExist:
            follow_request_reverse = None

        if follow_request_reverse:
            Request.objects.remove_received_follow_request(from_profile=n.user_id, to_profile=m.user_id)

        # Ver si seguimos al perfil que vamos a bloquear

        if n.follow.is_connected(m):
            m.follow.disconnect(n)
            n.follow.disconnect(m)

        m.bloq.connect(n)  # Creamos relacion de bloqueo

        response = True

        print('response: %s, haslike: %s, status: %s' % (response, haslike, status))
        data = {'response': response, 'haslike': haslike, 'status': status}
        return HttpResponse(json.dumps(data), content_type='application/json')


@login_required(login_url='/')
def welcome_view(request, username):
    """
    View para pagina de bienvenida despues
    del registro.
    """
    user_profile = get_object_or_404(get_user_model(),
                                     username__iexact=username)
    user = request.user

    if user_profile.pk != user.pk:
        raise Http404

    return render(request, 'account/nuevosusuarios.html', {'user_profile': user})


@login_required(login_url='/')
@ensure_csrf_cookie
def welcome_step_1(request):
    """
    View para seleccionar los intereses
    del usuario registrado.
    """
    user = request.user
    user_node = NodeProfile.nodes.get(user_id=user.id)

    context = {'user_profile': user}

    if request.method == 'POST':
        response = "success"
        # Procesar temas escritos por el usuario
        tags = request.POST.getlist('tags[]')
        for tag in tags:
            if tag.isspace():
                response = "with_spaces"
                return HttpResponse(json.dumps(response), content_type='application/json')
            interest = TagProfile.nodes.get_or_none(title=tag)
            if not interest and tag:
                interest = TagProfile(title=tag).save()
            if interest:
                interest.user.connect(user_node)
        # Procesar temas por defecto
        choices = request.POST.getlist('choices[]')
        if not tags and not choices:
            response = "empty"
            return HttpResponse(json.dumps(response), content_type='application/json')
        for choice in choices:
            value = dict(ThemesForm.CHOICES).get(choice)
            interest = TagProfile.nodes.get_or_none(title=value)
            if not interest and value:
                interest = TagProfile(title=value).save()
            if interest:
                interest.user.connect(user_node)
        return HttpResponse(json.dumps(response), content_type='application/json')
    else:
        results, meta = db.cypher_query(
            "MATCH (n:NodeProfile)-[:INTEREST]-(interest:TagProfile) RETURN interest.title, COUNT(interest) AS score ORDER BY score DESC LIMIT 10")
        context['top_tags'] = results
        context['form'] = ThemesForm

    return render(request, 'account/welcomestep1.html', context)


@login_required(login_url='/')
def set_first_Login(request):
    """
    Establece si el usuario se ha logueado por primera vez
    """
    print('>>> SET_FIRST_LOGIN')
    user = request.user
    if request.method == 'POST':
        print('>>> IS_POST')
        if user.profile.is_first_login:
            user.profile.is_first_login = False
    else:  # ON GET ETC...
        return redirect('user_profile:profile', username=user.username)


class RecommendationUsers(ListView):
    """
        Lista de usuarios recomendados segun
        los intereses del usuario.
    """
    model = User
    template_name = "account/reccomendation_after_login.html"

    def get_queryset(self):
        user = self.request.user
        results, meta = db.cypher_query(
            "MATCH (u1:NodeProfile)-[:INTEREST]->(tag:TagProfile)<-[:INTEREST]-(u2:NodeProfile) WHERE u1.user_id=%d AND NOT u2.privacity='N' RETURN u2, COUNT(tag) AS score ORDER BY score DESC LIMIT 50" % user.id)
        users = [NodeProfile.inflate(row[0]) for row in results]
        if not users:
            users = NodeProfile.nodes.filter(privacity__ne='N', user_id__ne=user.id).order_by('?')[:50]

        return users

    def get_context_data(self, **kwargs):
        context = super(RecommendationUsers, self).get_context_data(**kwargs)
        context['user_profile'] = self.request.user
        return context


recommendation_users = login_required(RecommendationUsers.as_view(), login_url='/')


class LikeListUsers(AjaxListView):
    """
    Lista de usuarios que han dado like a un perfil
    """
    model = User
    template_name = "account/like_list.html"
    context_object_name = "object_list"
    page_template = "account/like_entries.html"

    def get_queryset(self):
        username = self.kwargs['username']

        n = NodeProfile.nodes.get(title=username)
        return n.get_like_to_me()

    def get_context_data(self, **kwargs):
        context = super(LikeListUsers, self).get_context_data(**kwargs)
        context['user_profile'] = self.kwargs['username']
        user = self.request.user

        return context


like_list = login_required(LikeListUsers.as_view(), login_url='/')


class UserAutocomplete(autocomplete.Select2QuerySetView):
    """
    Autocompletado de usuarios
    """

    def get_queryset(self):
        if not self.request.user.is_authenticated():
            return User.objects.none()

        users = User.objects.all()

        if self.q:
            users = users.filter(username__istartswith=self.q)

        return users


def search_users(request):
    """
    Busqueda de usuarios por AJAX,
    para el autocompletado sin tener que entrar
    en el template de busqueda
    """
    user = request.user

    if user.is_authenticated() and request.is_ajax():
        value = request.GET.get('value', None)

        query = User.objects.filter(
            Q(username__icontains=value) | Q(first_name__icontains=value) | Q(last_name__icontains=value))[:20]
        result = []
        for user in query:
            user_json = {}
            user_json['username'] = user.username
            user_json['first_name'] = user.first_name
            user_json['last_name'] = user.last_name
            user_json['avatar'] = get_author_avatar(user.id)
            result.append(user_json)

        return JsonResponse({'result': result})

class SearchUsuarioView(SearchView):
    # formview
    template_name = 'search/search.html'
    queryset = SearchQuerySet().all()
    form_class = SearchForm

    def get_queryset(self):
        queryset = super(SearchUsuarioView, self).get_queryset()
        models = []
        try:
            criteria = self.kwargs['option']
        except KeyError:
            criteria = 'all'

        if criteria == 'all':
            models.append(User)
            models.append(Publication)
            models.append(Photo)
            models.append(PublicationVideo)
        if criteria == 'accounts':
            models.append(User)
        if criteria == 'publications':
            models.append(Publication)
        if criteria == 'images':
            models.append(Photo)
        if criteria == 'videos':
            models.append(PublicationVideo)

        q = self.request.GET['q']
        self.initial = {'q': q, 's': criteria}

        if models:
            return queryset.filter(content=q).models(*models)
        else:
            # aqui levantar una excepcion
            return None

    def get_context_data(self, **kwargs):
        ctx = super(SearchUsuarioView, self).get_context_data(**kwargs)
        try:
            ctx['tab'] = self.kwargs['option']
        except KeyError:
            ctx['tab'] = 'all'
        ctx['object_list'] = self.queryset
        ctx['searchForm'] = self.form_class(self.initial)
        ctx['q'] = self.initial['q']
        ctx['s'] = self.initial['s']
        return ctx


@login_required(login_url='/')
def recommendation_real_time(request):
    if request.method == 'POST':
        user = request.user
        results, meta = db.cypher_query(
            "MATCH (u1:NodeProfile)-[:INTEREST]->(tag:TagProfile)<-[:INTEREST]-(u2:NodeProfile) WHERE u1.user_id=%d AND NOT u2.privacity='N' RETURN u2.title, u2.user_id, u2.first_name, u2.last_name, COUNT(tag) AS score ORDER BY score DESC LIMIT 50" % user.id)
        users = []
        [users.append({'id': x[1], 'title': x[0]}) for x in results]
        return JsonResponse(users, safe=False)

    return JsonResponse({'response': None})
