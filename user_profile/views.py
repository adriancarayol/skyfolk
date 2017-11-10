import json
import logging

from allauth.account.views import PasswordChangeView, EmailView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, ViewDoesNotExist
from django.core.urlresolvers import reverse_lazy
from django.db import transaction, IntegrityError
from django.db.models import Case, When, Value, IntegerField, OuterRef, Subquery
from django.db.models import Count
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView
from django.views.generic.edit import FormView, UpdateView
from django.views.generic.list import ListView
from el_pagination.views import AjaxListView
from haystack.generic_views import SearchView
from haystack.query import SearchQuerySet, SQ, RelatedSearchQuerySet
from neomodel import db
from rest_framework import generics
from rest_framework.renderers import JSONRenderer

from avatar.templatetags.avatar_tags import avatar, avatar_url
from notifications.models import Notification
from notifications.signals import notify
from photologue.models import Photo
from publications.forms import PublicationForm, PublicationEdit, SharedPublicationForm
from publications.models import Publication, PublicationVideo
from user_profile.decorators import user_can_view_profile_info
from user_profile.forms import AdvancedSearchForm
from user_profile.forms import ProfileForm, UserForm, \
    SearchForm, PrivacityForm, DeactivateUserForm, ThemesForm
from user_profile.models import Request, Profile, \
    RelationShipProfile, FOLLOWING, NotificationSettings, BLOCK
from user_profile.node_models import NodeProfile, TagProfile
from utils.ajaxable_reponse_mixin import AjaxableResponseMixin
from .serializers import UserSerializer
from .utils import crop_image, make_pagination_html
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def load_profile_publications(request, page, profile):
    """
    Devuelve los comentarios de un perfil
    """
    user = request.user

    shared_publications = Publication.objects.filter(shared_publication__id=OuterRef('pk'),
                                                     deleted=False).order_by().values(
        'shared_publication__id')

    total_shared_publications = shared_publications.annotate(c=Count('*')).values('c')

    shared_for_me = shared_publications.annotate(have_shared=Count(Case(
        When(author_id=user.id, then=Value(1))
    ))).values('have_shared')

    users_not_blocked_me = RelationShipProfile.objects.filter(
        to_profile=user.profile, type=BLOCK).values('from_profile_id')

    pubs = Publication.objects.filter(
        ~Q(author__profile__in=users_not_blocked_me) &
        Q(board_owner_id=profile.id) & Q(level__lte=0) & Q(
            deleted=False)).prefetch_related('extra_content', 'images',
                                             'videos', 'shared_publication__images',
                                             'tags',
                                             'shared_publication__author',
                                             'shared_group_publication__images',
                                             'shared_group_publication__author',
                                             'shared_group_publication__videos',
                                             'shared_group_publication__group_extra_content',
                                             'shared_publication__videos', 'shared_publication__extra_content') \
        .select_related('author',
                        'board_owner', 'shared_publication',
                        'parent', 'shared_group_publication').annotate(
        likes=Count('user_give_me_like'),
        hates=Count('user_give_me_hate')).annotate(have_like=Count(Case(
        When(user_give_me_like__id=user.id, then=Value(1)),
        output_field=IntegerField()
    )), have_hate=Count(Case(
        When(user_give_me_hate__id=user.id, then=Value(1)),
        output_field=IntegerField()
    ))).annotate(total_shared=Subquery(total_shared_publications, output_field=IntegerField())).annotate(
        have_shared=Subquery(shared_for_me, output_field=IntegerField()))

    try:
        paginator = Paginator(pubs, 25)
        try:
            publications = paginator.page(page)
        except PageNotAnInteger:
            publications = paginator.page(1)
        except EmptyPage:
            publications = paginator.page(paginator.num_pages)

    except Exception as e:
        publications = []
        logging.info(e)

    return publications


def profile_view_ajax(request, user_profile, node_profile=None):
    """
    Vista AJAX para paginacion
    de la vista profile
    """
    qs = request.GET.get('qs', None)

    if not qs:
        raise ViewDoesNotExist('Parametro QS no encontrado')

    if qs == 'publications':
        page = request.GET.get('page', 1)
        template = 'account/profile_comments.html'
        publications = load_profile_publications(request, page, user_profile)
        context = {
            'user_profile': user_profile,
            'publications': publications
        }
    elif qs == 'following':
        page = int(request.GET.get('page', 1))
        template = 'account/follow_entries.html'
        profile = Profile.objects.values_list('id', flat=True).get(user=request.user)

        following_list = RelationShipProfile.objects.filter(
            from_profile=profile,
            type=FOLLOWING).values('to_profile_id')

        users = User.objects.filter(profile__in=following_list)
        paginator = Paginator(users, 25)  # Show 25 contacts per page

        try:
            followed = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            followed = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            followed = paginator.page(paginator.num_pages)

        context = {
            'user_profile': user_profile,
            'friends_top12': followed,
            'friend_page': page,
        }
    else:
        raise ValueError('No existe el querystring %s' % qs[:25])

    return render(request, template_name=template, context=context)


@login_required(login_url='/')
def profile_view(request, username,
                 template="account/profile.html"):
    """
    Vista principal del perfil de usuario.
    :param username:
    :param template: Template por defecto que muestra el perfil
    :param request:
    """
    user = request.user
    user_profile = get_object_or_404(User.objects.select_related('profile'),
                                     username__iexact=username)

    try:
        n = NodeProfile.nodes.get(user_id=user_profile.id)
        m = NodeProfile.nodes.get(user_id=user.id)
    except NodeProfile.DoesNotExist:
        raise Http404

    context = {}
    # Privacidad del usuario
    privacity = n.is_visible(m)

    # Si es una peticion AJAX (cargar skyline, seguidos...)
    if request.is_ajax():
        if privacity and privacity != 'all':
            pass
        else:
            return profile_view_ajax(request, user_profile, node_profile=n)

    context['user_profile'] = user_profile
    context['privacity'] = privacity

    # Recuperamos requests para el perfil y si el perfil es gustado.
    if user.username != username:
        try:
            liked = m.has_like(to_like=user_profile.id)
        except Exception:
            liked = False
    else:
        liked = False

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
    # Comprobamos si existe una peticion de seguimiento
    try:
        friend_request = Request.objects.get_follow_request(from_profile=user.id, to_profile=user_profile.id)
    except ObjectDoesNotExist:
        friend_request = None

    # Cuando no tenemos permisos suficientes para ver nada del perfil
    if privacity == "nothing":
        context['isBlocked'] = isBlocked
        context['liked'] = liked
        context['isFollower'] = isFollower
        context['isFriend'] = isFollow
        context['existFollowRequest'] = True if friend_request else False
        template = "account/privacity/private_profile.html"
        return render(request, template, context)
    elif n.bloq.is_connected(m):
        template = "account/privacity/block_profile.html"
        context['isBlocked'] = isBlocked
        context['liked'] = liked
        return render(request, template, context)

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

    # Recuperamos el numero de contenido multimedia que tiene el perfil
    try:
        if user.username == username:
            multimedia_count = user_profile.profile.get_total_num_multimedia()
        else:
            multimedia_count = user_profile.profile.get_num_multimedia()
    except ObjectDoesNotExist:
        multimedia_count = 0

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

    context['publicationForm'] = PublicationForm()
    context['publication_edit'] = PublicationEdit()
    context['publication_shared'] = SharedPublicationForm()

    # Cargamos las publicaciones del perfil
    publications = load_profile_publications(request, 1, user_profile)

    # Contenido de las tres tabs
    context['publications'] = publications
    context['component'] = 'react/publications.js'
    context['friend_page'] = 1

    return render(request, template, context)


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
        profile = Profile.objects.get(user_id=user.id)
    except ObjectDoesNotExist:
        raise Http404

    logging.info('>>>>> PETICION CONFIG - User: {}'.format(user.username))
    if request.POST:
        privacity_form = PrivacityForm(data=request.POST)
        if privacity_form.is_valid():
            try:
                with transaction.atomic(using="default"):
                    with db.transaction:
                        privacity = privacity_form.clean_privacity()
                        user_profile.privacity = privacity
                        profile.privacity = privacity
                        user_profile.save()
                        profile.save()
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
    user_profile = Profile.objects.select_related('user').get(user=request.user)
    logging.info('>>>>>>>  PETICION CONFIG')
    if request.POST:
        # formulario enviado
        logging.info('>>>>>>>  paso 1' + str(request.FILES))
        user_form = UserForm(data=request.POST, instance=request.user)
        perfil_form = ProfileForm(request.POST, request.FILES or None, request=request)
        if user_form.is_valid() and perfil_form.is_valid():
            # formulario validado correctamente
            try:
                with transaction.atomic(using='default'):
                    data = perfil_form.clean_backImage()
                    if data:
                        file = crop_image(data, "cover-%s.jpge" % request.user.username, request)
                        user_profile.back_image = file
                    user_profile.status = perfil_form.clean_status()
                    user_profile.save()
                    user_form.save()
                    logging.info('>>>>>>  save')
                    data = {
                        'result': True,
                        'state': 200,
                        'message': 'Success',
                        'gallery': '/config/profile'
                    }
                    return JsonResponse({'data': data})
            except Exception as e:
                logging.info(
                    "No se pudo guardar la configuracion del perfil de la cuenta: {}".format(request.user.username))
                data = {
                    'result': False,
                    'state': 500,
                    'message': 'Success'
                }

                return JsonResponse({'data': data})
    else:
        # formulario inicial
        user_form = UserForm(instance=request.user)
        perfil_form = ProfileForm(initial={'status': user_profile.status})

    logging.Manager('>>>>>>>  paso x')
    context = {'showPerfilButtons': True,
               'user_profile': user_profile,
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
    id_users = [u.user_id for u in n.bloq.match()]
    list_blocked = User.objects.filter(id__in=id_users).select_related('profile')

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
            except NodeProfile.DoesNotExist:
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
                try:
                    with transaction.atomic(using="default"):
                        with db.transaction:
                            sql_friend = User.objects.select_related('profile').get(id=friend.user_id)
                            emitter = Profile.objects.get(user_id=user_request.id)
                            RelationShipProfile.objects.create(to_profile=sql_friend.profile,
                                                               from_profile=emitter, type=FOLLOWING)
                            data['response'] = 'added_friend'
                except Exception as e:
                    logging.info(e)

                data['friend_username'] = friend.title
                data['friend_avatar'] = avatar(sql_friend)
                data['friend_first_name'] = sql_friend.first_name
                data['friend_last_name'] = sql_friend.last_name
                return HttpResponse(json.dumps(data), content_type='application/javascript')

            # enviamos peticion de amistad
            try:
                friend_request = Request.objects.get_follow_request(from_profile=user.user_id,
                                                                    to_profile=friend.user_id)
            except ObjectDoesNotExist:
                friend_request = None

            if not friend_request:
                # Eliminamos posibles notificaciones residuales
                sql_friend = User.objects.get(id=friend.user_id)
                Notification.objects.filter(actor_object_id=user_request.pk,
                                            recipient=sql_friend,
                                            level='friendrequest').delete()
                # Enviamos la notificacion
                notification = notify.send(user_request, actor=User.objects.get(pk=user_request.pk).username,
                                           recipient=sql_friend,
                                           verb=u'<a href="/profile/{0}/">@{0}</a> quiere seguirte.'.format(
                                               user_request.title),
                                           level='friendrequest')
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
            except NodeProfile.DoesNotExist:
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
                try:
                    with transaction.atomic(using="default"):
                        with db.transaction:
                            sql_friend = User.objects.select_related('profile').get(id=friend.user_id)
                            emitter = Profile.objects.get(user_id=user_request.id)
                            RelationShipProfile.objects.create(to_profile=sql_friend.profile,
                                                               from_profile=emitter, type=FOLLOWING)
                            data['response'] = 'added_friend'
                except Exception as e:
                    logging.info(e)
                    return HttpResponse(json.dumps(data), content_type='application/javascript')

                data['friend_username'] = friend.title
                data['friend_avatar'] = avatar(sql_friend)
                data['friend_first_name'] = sql_friend.first_name
                data['friend_last_name'] = sql_friend.last_name
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
                sql_friend = User.objects.get(id=friend.user_id)
                Notification.objects.filter(actor_object_id=user_request.pk,
                                            recipient=sql_friend,
                                            level='friendrequest').delete()
                # Enviamos nueva notificacion
                notification = notify.send(user_request, actor=User.objects.get(pk=user_request.pk).username,
                                           recipient=sql_friend,
                                           verb=u'<a href="/profile/{0}/">@{0}</a> quiere seguirte.'.format(
                                               user_request.title), level='friendrequest')
                # Enlazamos notificacion y peticion de amistad
                try:
                    Request.objects.add_follow_request(user.user_id, friend.user_id, notification[0][1])
                    response = 'new_petition'
                except ObjectDoesNotExist:
                    response = "no_added_friend"

    sql_friend = User.objects.get(id=friend.user_id)
    data['response'] = response
    data['friend_username'] = sql_friend.username
    data['friend_avatar'] = avatar(sql_friend)
    data['friend_first_name'] = sql_friend.first_name
    data['friend_last_name'] = sql_friend.last_name
    return HttpResponse(json.dumps(data), content_type='application/javascript')


@login_required(login_url='/')
def like_profile(request):
    """
    Funcion para dar like al perfil
    """
    response = "null"
    if request.method == 'POST':
        user = request.user
        slug = request.POST.get('slug', None)

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
                        notify.send(user, actor=user.username,
                                    recipient=actual_profile,
                                    description="@{0} ha dado like a tu perfil.".format(user.username),
                                    verb=u'¡<a href="/profile/%s">@%s</a> te ha dado me gusta a tu perfil!.' % (
                                        user.username, user.username), level='like_profile')
                response = "like"
            except Exception as e:
                pass

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
        slug = request.POST.get('slug', None)

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
                try:
                    with transaction.atomic(using="default"):
                        with db.transaction:
                            recipient = User.objects.select_related('profile').get(id=m.user_id)
                            emitter = Profile.objects.get(user_id=user.id)
                            RelationShipProfile.objects.create(to_profile=recipient.profile,
                                                               from_profile=emitter, type=FOLLOWING)
                            # enviamos notificacion informando del evento
                            notify.send(user, actor=n.title,
                                        recipient=recipient,
                                        description="@{0} ahora es tu seguidor.".format(user.username),
                                        verb=u'¡ahora te sigue <a href="/profile/%s">%s</a>!.' % (n.title, n.title),
                                        level='new_follow')
                    response = "added_friend"
                except Exception as e:
                    logging.info(e)
                    response = "no_added_friend"

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
                                           description="@{0} quiere seguirte.".format(n.title),
                                           verb=u'<a href="/profile/{0}/">@{0}</a> quiere seguirte.'.format(n.title),
                                           level='friendrequest')

                # Enlazamos notificacion con peticion de amistad
                try:
                    Request.objects.add_follow_request(n.user_id,
                                                       m.user_id,
                                                       notification[0][1])

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
        profile_user_id = request.POST.get('slug', None)
        request_status = request.POST.get('status', None)

        try:
            recipient = User.objects.select_related('profile').get(id=profile_user_id)
            emitter = Profile.objects.get(user_id=user.id)
        except ObjectDoesNotExist:
            return HttpResponse(json.dumps(response), content_type='application/javascript')

        if request_status == 'accept':
            try:
                with transaction.atomic(using="default"):
                    with db.transaction:
                        RelationShipProfile.objects.create(to_profile=emitter,
                                                           from_profile=recipient.profile, type=FOLLOWING)
                        notify.send(user, actor=user.username,
                                    recipient=recipient,
                                    description="@{0} ha aceptado tu solicitud de seguimiento.".format(user.username),
                                    verb=u'¡ahora sigues a <a href="/profile/%s">%s</a>!.' % (
                                        user.username, user.username),
                                    level='new_follow')

                        Request.objects.remove_received_follow_request(from_profile=recipient.id,
                                                                       to_profile=user.id)

                response = "added_friend"
                logging.info('user.profile: {} emitter_profile: {}'.format(user.username, recipient.id))
                # enviamos notificacion informando del evento
            except Exception as e:
                logging.info(e)
                response = 'rejected'

        elif request_status == 'rejected':
            try:
                with transaction.atomic(using="default"):
                    Request.objects.remove_received_follow_request(from_profile=recipient.id,
                                                                   to_profile=user.id)
                response = "rejected"
            except Exception as e:
                response = "null"
        else:
            response = "rejected"

    return HttpResponse(json.dumps(response), content_type='application/javascript')


# Elimina relación entre dos usuarios
@login_required(login_url='/')
def remove_relationship(request):
    """
    Elimina relacion seguidor/seguido
    """
    response = None
    user = request.user
    slug = request.POST.get('slug', None)

    if request.method == 'POST':
        try:
            profile_user = NodeProfile.nodes.get(user_id=slug)
            me = NodeProfile.nodes.get(user_id=user.id)
        except NodeProfile.DoesNotExist:
            return HttpResponse(json.dumps(response), content_type='application/javascript')

        if me.follow.is_connected(profile_user):
            try:
                with transaction.atomic(using="default"):
                    with db.transaction:
                        emitter = Profile.objects.get(user_id=user.id)
                        recipient = Profile.objects.get(user_id=slug)
                        RelationShipProfile.objects.filter(to_profile=recipient,
                                                           from_profile=emitter, type=FOLLOWING).delete()
                response = True
            except Exception as e:
                logging.info(e)
                response = None

    return HttpResponse(json.dumps(response), content_type='application/javascript')


@login_required(login_url='/')
def remove_blocked(request):
    """
    Elimina relacion de bloqueo
    """
    response = None
    user = request.user
    slug = request.POST.get('slug', None)

    if request.method == 'POST':
        try:
            m = NodeProfile.nodes.get(user_id=user.id)
            n = NodeProfile.nodes.get(user_id=slug)
        except NodeProfile.DoesNotExist:
            return HttpResponse(json.dumps(response), content_type='application/javascript')

        try:
            if m.bloq.is_connected(n):
                emitter = Profile.objects.get(user_id=user.id)
                recipient = Profile.objects.get(user_id=slug)
                with transaction.atomic(using="default"):
                    with db.transaction:
                        RelationShipProfile.objects.filter(to_profile=recipient, from_profile=emitter,
                                                           type=BLOCK).delete()
                response = True
            else:
                logging.info('%s no tiene bloqueado a %s' % (m.title, n.title))
                response = False
        except Exception as e:
            logging.info(e)
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
    slug = request.POST.get('slug', None)
    status = request.POST.get('status', None)

    logging.info('REMOVE REQUEST FOLLOW: u1: {} - u2: {}'.format(user.id, slug))
    if request.method == 'POST':
        if status == 'cancel':
            try:
                with transaction.atomic(using="default"):
                    response = Request.objects.remove_received_follow_request(from_profile=user.id, to_profile=slug)
            except (ObjectDoesNotExist, IntegrityError) as e:
                response = False
            response = True
        else:
            response = False
        logging.info('Response -> ' + str(response))
    return HttpResponse(json.dumps(response), content_type='application/javascript')


class FollowersListView(ListView):
    """
    Lista de seguidores del usuario
    """
    context_object_name = "friends_top4"
    template_name = "account/relations.html"
    paginate_by = 25

    @method_decorator(user_can_view_profile_info)
    def dispatch(self, request, *args, **kwargs):
        return super(FollowersListView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        followers_list = RelationShipProfile.objects.filter(to_profile__user__username=self.kwargs.get('username', None),
                                                            type=FOLLOWING).values('from_profile_id')
        return User.objects.filter(profile__id=followers_list).select_related(
            'profile')

    def get_context_data(self, **kwargs):
        context = super(FollowersListView, self).get_context_data(**kwargs)
        context['url_name'] = "followers"
        context['component'] = 'react/followers_react.js'
        context['username'] = self.kwargs.get('username', None)
        return context


followers = login_required(FollowersListView.as_view())


class FollowingListView(ListView):
    """
    Lista de seguidos del usuario
    """
    context_object_name = "friends_top4"
    template_name = "account/relations.html"
    paginate_by = 25

    @method_decorator(user_can_view_profile_info)
    def dispatch(self, request, *args, **kwargs):
        return super(FollowingListView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        following_list = RelationShipProfile.objects.filter(from_profile__user__username=self.kwargs.get('username', None),
                                                            type=FOLLOWING).values('to_profile_id')
        return User.objects.filter(profile__in=following_list).select_related(
            'profile')

    def get_context_data(self, **kwargs):
        context = super(FollowingListView, self).get_context_data(**kwargs)
        context['url_name'] = "following"
        context['component'] = 'react/following_react.js'
        context['username'] = self.kwargs.get('username', None)
        return context


following = login_required(FollowingListView.as_view())


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
        emitter = Profile.objects.get(user_id=user.id)
        recipient = Profile.objects.get(user_id=id_user)
        if m.follow.is_connected(n):
            try:
                with transaction.atomic(using="default"):
                    with db.transaction:
                        RelationShipProfile.objects.filter(to_profile=recipient,
                                                           from_profile=emitter, type=FOLLOWING).delete()
                        RelationShipProfile.objects.filter(to_profile=emitter,
                                                           from_profile=recipient, type=FOLLOWING).delete()
                status = "isfollow"
            except Exception as e:
                logging.info(e)
                response = False
                data = {'response': response, 'haslike': haslike, 'status': status}
                return HttpResponse(json.dumps(data), content_type='application/json')

        # Ver si hay una peticion de "seguir" pendiente (al perfil contrario)
        try:
            follow_request_reverse = Request.objects.get_follow_request(from_profile=n.user_id, to_profile=m.user_id)
        except ObjectDoesNotExist:
            follow_request_reverse = None

        if follow_request_reverse:
            Request.objects.remove_received_follow_request(from_profile=n.user_id, to_profile=m.user_id)

        # Ver si seguimos al perfil que vamos a bloquear

        if n.follow.is_connected(m):
            try:
                with transaction.atomic(using="default"):
                    with db.transaction:
                        RelationShipProfile.objects.filter(to_profile=emitter,
                                                           from_profile=recipient, type=FOLLOWING).delete()
                        RelationShipProfile.objects.filter(to_profile=recipient,
                                                           from_profile=emitter, type=FOLLOWING).delete()
            except Exception as e:
                logging.info(e)
                response = False
                data = {'response': response, 'haslike': haslike, 'status': status}
                return HttpResponse(json.dumps(data), content_type='application/json')

        try:
            with transaction.atomic(using="default"):
                with db.transaction:
                    RelationShipProfile.objects.create(to_profile=recipient, from_profile=emitter, type=BLOCK)
        except Exception as e:
            logging.info(e)
            response = False
            data = {'response': response, 'haslike': haslike, 'status': status}
            return HttpResponse(json.dumps(data), content_type='application/json')

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
    user_profile = get_object_or_404(User,
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

    def __init__(self, *args, **kwargs):
        super(RecommendationUsers, self).__init__(*args, **kwargs)
        self.pagination = None

    def get_queryset(self):
        user = self.request.user
        current_page = int(self.request.GET.get('page', '1'))  # page or 1
        limit = 25 * current_page
        offset = limit - 25

        results, meta = db.cypher_query(
            "MATCH (u1:NodeProfile)-[:INTEREST]->(tag:TagProfile)<-[:INTEREST]-(u2:NodeProfile) WHERE u1.user_id=%d "
            "AND NOT u2.privacity='N' RETURN u2, COUNT(tag) AS score ORDER BY score DESC SKIP %d LIMIT %d" %
            (user.id, offset, 25))

        users = [NodeProfile.inflate(row[0]) for row in results]

        if not users:
            users = NodeProfile.nodes.filter(privacity__ne='N', user_id__ne=user.id).order_by('?')[offset:25]

        total_users = len(NodeProfile.nodes.all())
        total_pages = int(total_users / 25)
        if total_users % 25 != 0:
            total_pages += 1
        self.pagination = make_pagination_html(current_page, total_pages)

        user_ids = [u.user_id for u in users]
        return User.objects.filter(id__in=user_ids).select_related('profile')

    def get_context_data(self, **kwargs):
        context = super(RecommendationUsers, self).get_context_data(**kwargs)
        context['user_profile'] = self.request.user
        context['pagination'] = self.pagination
        return context


recommendation_users = login_required(RecommendationUsers.as_view(), login_url='/')


class LikeListUsers(AjaxListView):
    """
    Lista de usuarios que han dado like a un perfil
    """
    model = User
    template_name = "account/like_list.html"
    context_object_name = "object_list"

    def __init__(self, *args, **kwargs):
        super(LikeListUsers, self).__init__(*args, **kwargs)
        self.pagination = None

    @method_decorator(user_can_view_profile_info)
    def dispatch(self, request, *args, **kwargs):
        return super(LikeListUsers, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        username = self.kwargs['username']
        current_page = int(self.request.GET.get('page', '1'))  # page or 1
        limit = 25 * current_page
        offset = limit - 25

        n = NodeProfile.nodes.get(title=username)
        id_users = [u.user_id for u in n.get_like_to_me(offset=offset, limit=25)]

        total_users = n.count_likes()
        total_pages = int(total_users / 25)
        if total_users % 25 != 0:
            total_pages += 1
        self.pagination = make_pagination_html(current_page, total_pages)

        return User.objects.filter(id__in=id_users).select_related('profile')

    def get_context_data(self, **kwargs):
        context = super(LikeListUsers, self).get_context_data(**kwargs)
        context['user_profile'] = self.kwargs['username']
        context['pagination'] = self.pagination
        user = self.request.user

        return context


like_list = login_required(LikeListUsers.as_view(), login_url='/')


def autocomplete(request):
    """
    Autocompletado de usuarios
    """
    user = request.user
    q = request.GET.get('q', '')
    sqs = SearchQuerySet().models(Profile).filter(SQ(username=q) | SQ(firstname=q) | SQ(lastname=q))[:7]
    suggestions = [{'username': result.username, 'first_name': result.firstname,
                    'last_name': result.lastname, 'avatar': avatar(result.username)} for result in sqs]
    the_data = json.dumps({
        'results': suggestions
    })
    return HttpResponse(the_data, content_type='application/json')


class SearchUsuarioView(SearchView):
    template_name = 'search/search.html'
    form_class = SearchForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(SearchUsuarioView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        profile = Profile.objects.get(user_id=self.request.user.id)

        users_not_blocked_me = RelationShipProfile.objects.filter(
            to_profile=profile, type=BLOCK).values('from_profile_id')

        following = RelationShipProfile.objects.filter(Q(from_profile=profile) & ~Q(type=BLOCK)).values('to_profile_id')
        followers = RelationShipProfile.objects.filter(Q(to_profile=profile) & ~Q(type=BLOCK)).values('from_profile_id')

        queryset = RelatedSearchQuerySet().order_by('-pub_date').load_all().load_all_queryset(
            Publication, Publication.objects.filter((SQ(board_owner_id=self.request.user.id)
                                                     | SQ(author_id=self.request.user.id)) | (
                                                        (~SQ(
                                                            board_owner__profile__in=users_not_blocked_me) & ~SQ(
                                                            board_owner__profile__privacity='N') & ~SQ(
                                                            author__profile__in=users_not_blocked_me)) &
                                                        ((SQ(board_owner__profile__privacity='A') | (
                                                            (SQ(board_owner__profile__privacity='OF') &
                                                             SQ(
                                                                 board_owner__profile__in=following)) | (
                                                                SQ(board_owner__profile__privacity='OFAF') &
                                                                (SQ(
                                                                    board_owner__profile__in=following) | SQ(
                                                                    board_owner__profile__in=followers))
                                                            )) & ((SQ(author__profile__privacity='OF') &
                                                                   SQ(
                                                                       author__profile__in=following)) | (
                                                                      SQ(author__profile__privacity='OFAF') &
                                                                      (SQ(
                                                                          author__profile__in=following) | SQ(
                                                                          author__profile__in=followers))
                                                                  ) | SQ(author__profile__privacity='A'))) | (
                                                             SQ(author__profile__privacity='A') | (
                                                                 (SQ(author__profile__privacity='OF') &
                                                                  SQ(
                                                                      author__profile__in=following)) | (
                                                                     SQ(author__profile__privacity='OFAF') &
                                                                     (SQ(
                                                                         author__profile__in=following) | SQ(
                                                                         author__profile__in=followers))
                                                                 )) & ((SQ(board_owner__profile__privacity='OF') &
                                                                        SQ(
                                                                            board_owner__profile__in=following)) | (
                                                                           SQ(board_owner__profile__privacity='OFAF') &
                                                                           (SQ(
                                                                               board_owner__profile__in=following) | SQ(
                                                                               board_owner__profile__in=followers))
                                                                       ) | SQ(board_owner__profile__privacity='A')))))) \
                .select_related('author').prefetch_related('images')
        ).load_all_queryset(
            Photo, Photo.objects.filter(SQ(owner_id=self.request.user.id) |
                                        ((~SQ(owner__profile__privacity='N') & ~SQ(
                                            owner__profile__in=users_not_blocked_me))
                                         & ((SQ(owner__profile__privacity='OF') &
                                             SQ(owner__profile__in=following)
                                             & SQ(is_public=True))
                                            | (SQ(owner__profile__privacity='A') & SQ(is_public=True)) | (
                                                SQ(owner__profile__privacity='OFAF') & (
                                                    SQ(owner__profile__in=following) | SQ(
                                                        owner__profile__in=followers)))))) \
                .select_related('owner').prefetch_related('tags')
        ).load_all_queryset(
            Profile, Profile.objects.filter(SQ(user__is_active=True) & ~SQ(privacity='N')))

        models = []

        try:
            criteria = self.kwargs['option']
        except KeyError:
            criteria = 'all'

        if criteria == 'all':
            models.append(Profile)
            models.append(Publication)
            models.append(Photo)
        if criteria == 'accounts':
            models.append(Profile)
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
        ctx['searchForm'] = self.form_class(self.initial)
        ctx['q'] = self.initial['q']
        ctx['s'] = self.initial['s']

        return ctx


@login_required(login_url='/')
def recommendation_real_time(request):
    if request.method == 'POST':
        try:
            ids = json.loads(request.body.decode('utf-8'))
        except Exception:
            return JsonResponse({'response': None})

        if ids:
            exclude_ids = ','.join(str(e) for e in ids)
        else:
            exclude_ids = []

        if len(exclude_ids) > 100:
            exclude_ids = []

        user = request.user

        results, meta = db.cypher_query(
            "MATCH (u1:NodeProfile)-[:INTEREST]->(tag:TagProfile)<-[:INTEREST]-(u2:NodeProfile) WHERE u1.user_id=%d "
            "AND NOT u2.privacity='N' AND NOT (u2.user_id IN [%s]) RETURN u2.user_id, COUNT(tag) AS score ORDER BY "
            "score DESC LIMIT 50" % (
                user.id, exclude_ids))
        users = []

        if not results:
            ids.append(user.id)
            results = NodeProfile.nodes.exclude(privacity='N', user_id__in=ids).order_by('?')[:50]
            [users.append(x.user_id) for x in results]
        else:
            [users.append(x[0]) for x in results]

        sql_result = User.objects.filter(id__in=users)
        sql_users = []
        [sql_users.append({'id': u.id, 'username': u.username,
                           'first_name': u.first_name, 'last_name': u.last_name,
                           'avatar': avatar_url(u)}) for u in sql_result]
        return JsonResponse(sql_users, safe=False)

    return JsonResponse({'response': None})


class FollowingByAffinityList(generics.ListAPIView):
    serializer_class = UserSerializer
    renderer_classes = (JSONRenderer,)

    def get_queryset(self):
        user_id = self.request.user.id
        n = NodeProfile.nodes.get(user_id=user_id)
        pk_list = [u.user_id for u in n.get_favs_users()]
        preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(pk_list)])
        return User.objects.filter(id__in=pk_list).order_by(preserved)


class FollowersByAffinityList(generics.ListAPIView):
    serializer_class = UserSerializer
    renderer_classes = (JSONRenderer,)

    def get_queryset(self):
        user_id = self.request.user.id
        n = NodeProfile.nodes.get(user_id=user_id)
        pk_list = [u.user_id for u in n.get_favs_followers_users()]
        preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(pk_list)])
        return User.objects.filter(id__in=pk_list).order_by(preserved)


class NotificationSettingsView(AjaxableResponseMixin, UpdateView):
    model = NotificationSettings
    template_name = 'account/cf-notifications.html'
    fields = ['email_when_new_notification', 'email_when_recommendations', 'email_when_mp', 'followed_notifications',
              'followers_notifications', 'only_confirmed_users']
    success_url = '/config/notifications/'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(NotificationSettingsView, self).dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(NotificationSettings, user_id=self.request.user.id)

    def form_valid(self, form, msg=None):
        instance = form.save(commit=False)
        instance.user = self.request.user
        return super(NotificationSettingsView, self).form_valid(form)
