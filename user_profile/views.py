import json

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
from taggit.models import TaggedItem

from notifications.models import Notification
from notifications.signals import notify
from photologue.models import Photo
from publications.forms import PublicationForm, ReplyPublicationForm, PublicationEdit, SharedPublicationForm
from publications.models import Publication
from user_groups.forms import FormUserGroup
from user_profile.forms import AdvancedSearchForm
from user_profile.forms import ProfileForm, UserForm, \
    SearchForm, PrivacityForm, DeactivateUserForm, ThemesForm
from user_profile.models import UserProfile, AffinityUser
from publications.utils import get_author_avatar


@login_required(login_url='/')
@page_template("account/profile_comments.html")
@page_template("account/timeline_entries.html", key='timeline_entries')
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

    context = {}
    # Privacidad del usuario
    privacity = user_profile.profile.is_visible(user.profile)

    # Para escribir mensajes en mi propio perfil.
    self_initial = {'author': user.pk, 'board_owner': user.pk}
    group_initial = {'owner': user.pk}
    context['user_profile'] = user_profile
    context['searchForm'] = SearchForm(request.POST)
    context['privacity'] = privacity
    context['publicationSelfForm'] = PublicationForm(initial=self_initial)
    context['groupForm'] = FormUserGroup(initial=group_initial)
    context['notifications'] = user.notifications.unread()

    # Cuando no tenemos permisos suficientes para ver nada del perfil
    if privacity == "nothing":
        template = "account/privacity/private_profile.html"
        return render(request, template, context)
    elif privacity == "block":
        template = "account/privacity/block_profile.html"
        return render(request, template, context)

    # Recuperamos requests para el perfil y si el perfil es gustado.
    json_requestsToMe = None
    if user.username != username:
        liked = True
        try:
            user.profile.has_like(user_profile.profile)
        except ObjectDoesNotExist:
            liked = False
    else:
        liked = False
        requestsToMe = user.profile.get_received_friends_requests()

        if requestsToMe:
            requestsToMe_result = list()
            for item in requestsToMe:
                requestsToMe_result.append(
                    {'id_profile': item.pk, 'username': item.user.username, })
            json_requestsToMe = json.dumps(requestsToMe_result)

    # Recuperamos el numero de seguidores
    try:
        num_followers = user_profile.profile.get_followers().count()
    except ObjectDoesNotExist:
        num_followers = None

    # Recuperamos el numero de seguidos y la lista de seguidos
    try:
        num_follows = user_profile.profile.get_following()
    except ObjectDoesNotExist:
        num_follows = None

    # Comprobamos si el perfil esta bloqueado
    isBlocked = False
    if user.username != username:
        try:
            if user.profile.is_blocked(user_profile.profile):
                isBlocked = True
        except ObjectDoesNotExist:
            pass

    # Comprobamos si el perfil es seguidor
    isFollower = False
    if user.username != username:
        try:
            if user.profile.is_follower(user_profile.profile):
                isFollower = True
        except ObjectDoesNotExist:
            pass
    # Comprobamos si el perfil es seguido
    isFollow = False
    if user.username != username:
        try:
            if user.profile.is_follow(user_profile.profile):
                isFollow = True
        except ObjectDoesNotExist:
            pass
    # Recuperamos el numero de contenido multimedia que tiene el perfil
    try:
        if user.username == username:
            multimedia_count = user_profile.profile.get_total_num_multimedia()
        else:
            multimedia_count = user_profile.profile.get_num_multimedia()
    except ObjectDoesNotExist:
        multimedia_count = 0
    # Comprobamos si existe una peticion de seguimiento
    try:
        friend_request = user.profile.get_follow_request(user_profile.profile)
    except ObjectDoesNotExist:
        friend_request = None

    context['json_requestsToMe'] = json_requestsToMe
    context['liked'] = liked
    context['n_likes'] = len(user_profile.profile.likesToMe.all())
    context['followers'] = num_followers
    context['following'] = len(num_follows)
    context['isBlocked'] = isBlocked
    context['isFollower'] = isFollower
    context['isFriend'] = isFollow
    context['multimedia_count'] = multimedia_count
    context['existFollowRequest'] = True if friend_request else False

    if privacity == "followers" or privacity == "both":
        template = "account/privacity/need_confirmation_profile.html"
        return render(request, template, context)

    # Para escribir mensajes en perfiles ajenos
    initial = {'author': user.pk, 'board_owner': user_profile.pk}
    context['reply_publication_form'] = ReplyPublicationForm(initial=initial)
    context['publicationForm'] = PublicationForm(initial=initial)
    context['publication_edit'] = PublicationEdit()
    context['publication_shared'] = SharedPublicationForm(initial=initial)

    # cargar lista comentarios
    try:
        # if user_profile.username == username:
        publications = [node.get_descendants(include_self=True).filter(deleted=False, level__lte=1)[:10]
                        for node in
                        Publication.objects.filter(
                            board_owner=user_profile, deleted=False,
                            parent=None)[:20]]
    except ObjectDoesNotExist:
        publications = None

    # Establece la afinidad al perfil visitado.
    if user.pk != user_profile.pk:
        AffinityUser.objects.check_limit(emitterid=user_profile.profile)
    try:
        if user.pk != user_profile.pk:
            profile_visit, created = AffinityUser.objects.get_or_create(emitter=user.profile,
                                                                        receiver=user_profile.profile)
        else:
            profile_visit, created = None, False
    except ObjectDoesNotExist:
        profile_visit, created = None, False

    if not created and profile_visit:
        profile_visit.save()

    # Contenido de las tres tabs
    context['publications'] = publications
    context['friends_top12'] = num_follows

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
    initial = {'author': user.pk, 'board_owner': user.pk}
    searchForm = SearchForm(request.POST)
    # mostrar formulario para enviar comentarios/publicaciones
    publicationForm = PublicationForm(initial=initial)
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
                       'publicationSelfForm': publicationForm,
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
                return render(request, 'account/search.html', {'showPerfilButtons': True, 'searchForm': searchForm,
                                                               'resultSearch': result_search,
                                                               'publicationSelfForm': publicationForm,
                                                               'resultMessages': result_messages,
                                                               'result_media': result_media,
                                                               'words': words,
                                                               'message': info,
                                                               'notifications': user.notifications.unread()})


@login_required(login_url='/')
def advanced_view(request):
    """
    Búsqueda avanzada
    """
    user = request.user
    template_name = "account/search-avanzed.html"
    initial = {'author': user.pk, 'board_owner': user.pk}
    publicationForm = PublicationForm(initial=initial)
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

    return render(request, template_name, {'publicationSelfForm': publicationForm, 'searchForm': searchForm,
                                           'form': form, 'notifications': user.notifications.unread()})


@login_required(login_url='/')
def config_privacity(request):
    user_profile = request.user
    initial = {'author': user_profile.pk, 'board_owner': user_profile.pk}
    publicationForm = PublicationForm(initial=initial)
    searchForm = SearchForm()
    print('>>>>> PETICION CONFIG')
    if request.POST:
        privacity_form = PrivacityForm(data=request.POST, instance=user_profile.profile)
        if privacity_form.is_valid():
            privacity_form.save()
            return HttpResponseRedirect('/config/privacity')
    else:
        privacity_form = PrivacityForm(instance=user_profile.profile)

    return render(request, 'account/cf-privacity.html',
                  {'showPerfilButtons': True, 'searchForm': searchForm, 'publicationSelfForm': publicationForm,
                   'privacity_form': privacity_form,
                   'notifications': user_profile.notifications.unread()})


@login_required(login_url='/')
def config_profile(request):
    user_profile = request.user
    initial = {'author': user_profile.pk, 'board_owner': user_profile.pk}
    publicationForm = PublicationForm(initial=initial)
    searchForm = SearchForm()
    print('>>>>>>>  PETICION CONFIG')
    if request.POST:
        # formulario enviado
        print('>>>>>>>  paso 1' + str(request.FILES))
        user_form = UserForm(data=request.POST, instance=request.user)
        perfil_form = ProfileForm(
            request.POST, request.FILES, instance=request.user.profile)

        print('>>>>>>>  paso 1.1')
        if user_form.is_valid() and perfil_form.is_valid():
            # formulario validado correctamente
            print('>>>>>>  save')
            user_form.save()
            perfil_form.save()
            # poner mas tarde, que muestre un mensaje de formulario aceptado
            return HttpResponseRedirect('/config/profile')

    else:
        # formulario inicial
        user_form = UserForm(instance=request.user)
        perfil_form = ProfileForm(instance=request.user.profile)

    print('>>>>>>>  paso x')
    context = {'showPerfilButtons': True, 'searchForm': searchForm,
               'user_profile': user_profile,
               'user_form': user_form, 'perfil_form': perfil_form,
               'publicationSelfForm': publicationForm,
               'notifications': user_profile.notifications.unread()}
    return render(request, 'account/cf-profile.html', context)
    # return render_to_response('account/cf-profile.html',
    # {'showPerfilButtons':True,'searchForm':searchForm,
    # 'user_form':user_form}, context_instance=RequestContext(request))


@login_required(login_url='/')
def config_pincode(request):
    user = request.user
    initial = {'author': user.pk, 'board_owner': user.pk}
    pin = user.profile.personal_pin
    publicationForm = PublicationForm(initial=initial)
    searchForm = SearchForm()

    context = {'showPerfilButtons': True, 'searchForm': searchForm,
               'publicationSelfForm': publicationForm, 'pin': pin,
               'notifications': user.notifications.unread()}

    return render(request, 'account/cf-pincode.html', context)


@login_required(login_url='/')
def config_blocked(request):
    user = request.user
    initial = {'author': user.pk, 'board_owner': user.pk}
    list_blocked = request.user.profile.get_blockeds()
    publicationForm = PublicationForm(initial=initial)
    searchForm = SearchForm()

    return render(request, 'account/cf-blocked.html', {'showPerfilButtons': True,
                                                       'searchForm': searchForm,
                                                       'publicationSelfForm': publicationForm,
                                                       'blocked': list_blocked,
                                                       'notifications': user.notifications.unread()})


@login_required(login_url='accounts/login')
def add_friend_by_username_or_pin(request):
    """
    Funcion para añadir usuario por nombre de usuario y perfil
    """
    print('ADD FRIEND BY USERNAME OR PIN')
    response = 'no_added_friend'
    friend = None
    data = {
        'response': response,
        'friend': friend
    }
    if request.method == 'POST':
        pin = str(request.POST.get('valor'))
        if len(pin) > 15:
            print('STEP 1')
            user_request = request.user
            user = user_request.profile
            print('STEP 2')
            print('Pin: {}'.format(pin))
            if str(user.personal_pin).strip() == pin.strip():
                return HttpResponse(json.dumps('your_own_pin'), content_type='application/javascript')
            else:
                print('personal_pin: {} pin: {}'.format(user.personal_pin, pin))

            try:
                friend = UserProfile.objects.get(personal_pin=pin)
            except ObjectDoesNotExist:
                data['response'] = 'no_match'
                return HttpResponse(json.dumps(data), content_type='application/javascript')

            if user.is_follow(friend):
                data['response'] = 'its_your_friend'
                data['friend'] = friend.user.username
                return HttpResponse(json.dumps(data), content_type='application/javascript')

            # Me tienen bloqueado
            is_blocked = friend.is_blocked(user)

            if is_blocked:
                data['response'] = 'user_blocked'
                data['friend'] = friend.user.username
                return HttpResponse(json.dumps(data), content_type='application/javascript')

            # Yo tengo bloqueado al perfil
            blocked_profile = user.is_blocked(friend)

            if blocked_profile:
                data['response'] = 'blocked_profile'
                data['friend'] = friend.user.username
                return HttpResponse(json.dumps(data), content_type='application/javascript')

            # Comprobamos si el usuario necesita peticion de amistad
            no_need_petition = friend.privacity == UserProfile.ALL
            if no_need_petition:
                created = user.add_direct_relationship(profile=friend)
                if created:
                    data['response'] = 'added_friend'
                    data['friend_username'] = friend.user.username
                    data['friend_avatar'] = get_author_avatar(friend.user)
                    data['friend_first_name'] = friend.user.first_name
                    data['friend_last_name'] = friend.user.last_name
                    return HttpResponse(json.dumps(data), content_type='application/javascript')

            # enviamos peticion de amistad
            try:
                friend_request = user.get_follow_request(friend)
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
                    created = user.add_follow_request(
                        friend, notification[0][1])
                    created.save()
                    response = 'new_petition'
                except ObjectDoesNotExist:
                    response = "no_added_friend"

        else:  # tipo == username
            user_request = request.user
            username = pin
            user = user_request.profile

            if user.user.username == username:
                data['response'] = 'your_own_username'
                return HttpResponse(json.dumps(data), content_type='application/javascript')

            try:
                friend = UserProfile.objects.get(user__username=username)
            except ObjectDoesNotExist:
                data['response'] = 'no_match'
                return HttpResponse(json.dumps(data), content_type='application/javascript')

            if user.is_follow(friend):  # if user.is_friend(friend):
                data['response'] = 'its_your_friend'
                data['friend'] = friend.user.username
                return HttpResponse(json.dumps(data), content_type='application/javascript')

            # Me tienen bloqueado
            is_blocked = friend.is_blocked(user)

            if is_blocked:
                data['response'] = 'user_blocked'
                data['friend'] = friend.user.username
                return HttpResponse(json.dumps(data), content_type='application/javascript')

            # Yo tengo bloqueado al perfil
            blocked_profile = user.is_blocked(friend)

            if blocked_profile:
                data['response'] = 'blocked_profile'
                data['friend'] = friend.user.username
                return HttpResponse(json.dumps(data), content_type='application/javascript')

            # Comprobamos si el usuario necesita peticion de amistad
            no_need_petition = friend.privacity == UserProfile.ALL
            if no_need_petition:
                created = user.add_direct_relationship(profile=friend)
                if created:
                    data['response'] = 'added_friend'
                    data['friend_username'] = friend.user.username
                    data['friend_avatar'] = get_author_avatar(friend.user)
                    data['friend_first_name'] = friend.user.first_name
                    data['friend_last_name'] = friend.user.last_name
                    return HttpResponse(json.dumps(data), content_type='application/javascript')

            # enviamos peticion de amistad
            try:
                friend_request = user.get_follow_request(
                    UserProfile.objects.get(user__username=username))
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
                    created = user.add_follow_request(
                        friend, notification[0][1])
                    created.save()
                    response = 'new_petition'
                except ObjectDoesNotExist:
                    response = "no_added_friend"

    data['response'] = response
    data['friend_username'] = friend.user.username
    data['friend_avatar'] = get_author_avatar(friend.user)
    data['friend_first_name'] = friend.user.first_name
    data['friend_last_name'] = friend.user.last_name
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
        actual_profile = get_object_or_404(UserProfile,
                                           id=slug)
        try:
            user_liked = user.profile.has_like(actual_profile)
        except ObjectDoesNotExist:
            user_liked = None

        if user_liked:
            user_liked.delete()
            affinity, created = AffinityUser.objects.get_or_create(emitter=user.profile, receiver=actual_profile)
            if not created:  # Quiere decir que ya ha interactuado con el perfil
                affinity.affinity -= 20
                affinity.save(increment=False)
            response = "nolike"
        else:
            print(str(slug))
            created = user.profile.add_like(actual_profile)
            created.save()
            affinity, created = AffinityUser.objects.get_or_create(emitter=user.profile, receiver=actual_profile)
            if not created:  # Quiere decir que ya ha interactuado con el perfil
                affinity.affinity += 20
                affinity.save(increment=False)
            response = "like"

    print('%s da like a %s' % (user.username, actual_profile.user.username))
    print('Nueva afinidad emitter: {} receiver: {} afinidad: {}'.format(user.username, actual_profile.user.username,
                                                                        affinity.affinity))
    print("Response: " + response)
    return HttpResponse(json.dumps(response), content_type='application/javascript')


# Request follow
@login_required(login_url='accounts/login')
def request_friend(request):
    """
    Funcion para solicitudes de amistad
    """
    print('>>>>>>> peticion amistad ')
    response = "null"
    if request.method == 'POST':
        user = request.user
        slug = request.POST.get('slug', None)
        profile = UserProfile.objects.get(pk=slug)

        # El perfil me ha bloqueado
        is_blocked = profile.is_blocked(user.profile)

        if is_blocked:
            response = "user_blocked"
            return HttpResponse(json.dumps(response), content_type='application/javascript')

        try:
            user_friend = user.profile.is_follow(profile)  # Comprobamos si YO ya sigo al perfil deseado.
        except ObjectDoesNotExist:
            user_friend = None

        if user_friend:
            response = "isfriend"
        else:
            # Comprobamos si el perfil necesita peticion de amistad
            no_need_petition = profile.privacity == UserProfile.ALL
            if no_need_petition:
                created = user.profile.add_direct_relationship(profile=profile)
                if created:
                    response = "added_friend"
                    # enviamos notificacion informando del evento
                    notify.send(user, actor=user.username,
                                recipient=profile.user,
                                verb=u'¡ahora te sigue <a href="/profile/%s">%s</a>!.' % (user.username, user.username),
                                level='new_follow')
                    return HttpResponse(json.dumps(response), content_type='application/javascript')
            response = "inprogress"
            try:
                friend_request = user.profile.get_follow_request(profile)
            except ObjectDoesNotExist:
                friend_request = None

            if not friend_request:
                # Eliminamos posibles notificaciones residuales
                Notification.objects.filter(actor_object_id=user.pk,
                                            recipient=profile.user,
                                            level='friendrequest').delete()
                # Creamos y enviamos la nueva notificacion
                notification = notify.send(user, actor=User.objects.get(pk=user.pk).username,
                                           recipient=profile.user,
                                           verb=u'quiere seguirte.', level='friendrequest')

                import pprint
                pprint.pprint(notification)
                # Enlazamos notificacion con peticion de amistad
                try:
                    created = user.profile.add_follow_request(
                        profile, notification[0][1])
                    created.save()
                except ObjectDoesNotExist:
                    response = "no_added_friend"

        print(response)

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
        profileUserId = request.POST.get('slug', None)
        request_status = request.POST.get('status', None)
        print('Respond friend request: ' + profileUserId + ' estado: ' + request_status)
        try:
            emitter_profile = User.objects.get(pk=profileUserId).profile
        except ObjectDoesNotExist:
            emitter_profile = None

        if emitter_profile:
            user.profile.remove_received_follow_request(emitter_profile)

            if request_status == 'accept':
                response = "not_added_friend"
                try:
                    user_friend = user.profile.is_follower(profileUserId)
                except ObjectDoesNotExist:
                    user_friend = None

                if not user_friend:
                    created = user.profile.add_follower(
                        emitter_profile)  # Me añado como seguidor del perfil que quiero seguir
                    created_2 = emitter_profile.add_follow(
                        user.profile)  # Añado a mi lista de "seguidos" al peril que quiero seguir
                    created.save()
                    created_2.save()

                    print('user.profile: {} emitter_profile: {}'.format(user.username, emitter_profile.user.username))

                    # enviamos notificacion informando del evento
                    notify.send(user, actor=user.username,
                                recipient=emitter_profile.user,
                                verb=u'¡ahora sigues a <a href="/profile/%s">%s</a>!.' % (user.username, user.username),
                                level='new_follow')

                    emitter_profile.remove_received_follow_request(
                        user.profile)  # ya podemos borrar la peticion de amistad

                    response = "added_friend"

            elif request_status == 'rejected':
                emitter_profile.remove_received_follow_request(user.profile)
                response = "rejected"
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
    profile_user = UserProfile.objects.get(pk=slug)

    if request.method == 'POST':
        try:
            user_friend = user.profile.is_follow(profile_user)  # Comprobamos si YO ya sigo al perfil deseado.
        except ObjectDoesNotExist:
            user_friend = None

        if user_friend:
            user.profile.remove_relationship(profile_user, 1)
            profile_user.remove_relationship(user.profile, 2)
            response = True
        else:
            response = False
    return HttpResponse(json.dumps(response), content_type='application/javascript')


@login_required(login_url='/')
def remove_blocked(request):
    """
    Elimina relacion de bloqueo
    """
    response = None
    user = request.user
    slug = request.POST.get('slug', None)
    profile_user = UserProfile.objects.get(pk=slug)
    print('%s ya no bloquea a %s' % (user.username, profile_user.user.username))
    print('>>>>> %s' % slug)
    if request.method == 'POST':
        try:
            blocked = user.profile.is_blocked(profile_user)
        except ObjectDoesNotExist:
            blocked = None

        if blocked:
            user.profile.remove_relationship(profile_user, 3)
            response = True
        else:
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
    profile_user = UserProfile.objects.get(pk=slug)
    print('REMOVE REQUEST FOLLOW')
    if request.method == 'POST':
        if status == 'cancel':
            user.profile.remove_received_follow_request(profile_user)
            response = True
        else:
            response = False
    print('Response -> ' + str(response))
    return HttpResponse(json.dumps(response), content_type='application/javascript')


# Load followers
@login_required(login_url='/')
def load_followers(request):
    """
    Funcion para cargar seguidores
    :return lista de seguidores:
    """
    print('>>>>>> PETICION AJAX, CARGAR MAS AMIGOS')
    friendslist = request.user.profile.get_followers()

    if friendslist is None:
        friends_next = None
    else:
        # friendslist = json.loads(friendslist)
        if request.method == 'POST':
            slug = request.POST.get('slug', None)
            print('>>>>>>> SLUG: ' + slug)
            n = int(slug) * 2
            # devolvera None si esta fuera de rango?
            friends_next = friendslist[n - 2:n]
            print('>>>>>>> LISTA: ')
            print(friends_next)
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
        user_profile = get_object_or_404(
            get_user_model(),
            username__iexact=self.kwargs['username'])
        return user_profile.profile.get_followers()

    def get_context_data(self, **kwargs):
        context = super(FollowersListView, self).get_context_data(**kwargs)
        user = self.request.user
        initial = {'author': user.pk, 'board_owner': user.pk}
        context['publicationSelfForm'] = PublicationForm(initial=initial)
        context['searchForm'] = SearchForm()
        context['url_name'] = "followers"
        context['notifications'] = user.notifications.unread()
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
        user_profile = get_object_or_404(
            get_user_model(),
            username__iexact=self.kwargs['username'])
        return user_profile.profile.get_following()

    def get_context_data(self, **kwargs):
        context = super(FollowingListView, self).get_context_data(**kwargs)
        user = self.request.user
        initial = {'author': user.pk, 'board_owner': user.pk}
        context['publicationSelfForm'] = PublicationForm(initial=initial)
        context['searchForm'] = SearchForm()
        context['url_name'] = "following"
        context['notifications'] = user.notifications.unread()
        return context


following = login_required(FollowingListView.as_view())


# Load follows
@login_required(login_url='/')
def load_follows(request):
    """
    Funcion para cargar mas seguidos
    :return lista de seguidos:
    """
    print('>>>>>> PETICION AJAX, CARGAR MAS AMIGOS')
    friendslist = request.user.profile.get_following()

    if friendslist is None:
        friends_next = None
    else:
        # friendslist = json.loads(friendslist)
        if request.method == 'POST':
            slug = request.POST.get('slug', None)
            print('>>>>>>> SLUG: ' + slug)
            n = int(slug) * 4
            # devolvera None si esta fuera de rango?
            friends_next = friendslist[n - 4:n]
            print('>>>>>>> LISTA: ')
            print(friends_next)
        else:
            friends_next = None
    return HttpResponse(json.dumps(list(friends_next)), content_type='application/json')


class PassWordChangeDone(TemplateView):
    template_name = 'account/confirmation_changepass.html'

    def get(self, request, *args, **kwargs):
        context = locals()
        user = self.request.user
        initial = {'author': user.pk, 'board_owner': user.pk}
        context['publicationSelfForm'] = PublicationForm(initial=initial)
        context['searchForm'] = SearchForm()
        context['showPerfilButtons'] = True
        context['notifications'] = user.notifications.unread()
        return render(request, self.template_name, context)


password_done = login_required(PassWordChangeDone.as_view())


# Modificacion del formulario para cambiar contraseña
class CustomPasswordChangeView(PasswordChangeView):
    success_url = reverse_lazy("account_done_password")

    def get_context_data(self, **kwargs):
        ret = super(PasswordChangeView, self).get_context_data(**kwargs)
        # NOTE: For backwards compatibility
        ret['password_change_form'] = ret.get('form')
        user = self.request.user
        initial = {'author': user.pk, 'board_owner': user.pk}
        ret['publicationSelfForm'] = PublicationForm(initial=initial)
        ret['searchForm'] = SearchForm()
        ret['showPerfilButtons'] = True
        ret['notifications'] = user.notifications.unread()
        # (end NOTE)
        return ret


custom_password_change = login_required(CustomPasswordChangeView.as_view())


# Modificacion del formulario para manejar los emails
class CustomEmailView(EmailView):
    def get_context_data(self, **kwargs):
        ret = super(EmailView, self).get_context_data(**kwargs)
        # NOTE: For backwards compatibility
        user = self.request.user
        initial = {'author': user.pk, 'board_owner': user.pk}
        ret['add_email_form'] = ret.get('form')
        ret['publicationSelfForm'] = PublicationForm(initial=initial)
        ret['searchForm'] = SearchForm()
        ret['showPerfilButtons'] = True
        ret['notifications'] = user.notifications.unread()
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
        context['publicationSelfForm'] = PublicationForm(initial=self_initial)
        context['searchForm'] = SearchForm()
        context['notifications'] = user.notifications.unread()
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = self.get_form(self.form_class)
        user = request.user

        if user.is_authenticated():
            if form.is_valid():
                user.is_active = not (form.clean_is_active())
                user.save()
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
        profileUserId = request.POST.get('id_user', None)

        try:
            emitter_profile = UserProfile.objects.get(pk=profileUserId)
        except ObjectDoesNotExist:
            response = False
            data = {'response': response, 'haslike': haslike}
            return HttpResponse(json.dumps(data), content_type='application/json')

        # Eliminar me gusta al perfil que se va a bloquear

        try:
            user_liked = user.profile.has_like(emitter_profile)
        except ObjectDoesNotExist:
            user_liked = None

        if user_liked:
            user_liked.delete()
            haslike = "liked"

        # Ver si hay una peticion de "seguir" pendiente
        try:
            follow_request = user.profile.get_follow_request(emitter_profile)
        except ObjectDoesNotExist:
            follow_request = None

        if follow_request:
            user.profile.remove_received_follow_request(emitter_profile)  # Eliminar peticion follow (user -> profile)
            status = "inprogress"

        # Ver si seguimos al perfil que vamos a bloquear
        is_follow = user.profile.is_follow(emitter_profile)

        if is_follow:
            user.profile.remove_relationship(emitter_profile, 1)  # Eliminar relacion follow
            emitter_profile.remove_relationship(user.profile, 2)  # Eliminar relacion follower
            status = "isfollow"

        # Ver si hay una peticion de "seguir" pendiente (al perfil contrario)
        try:
            follow_request_reverse = emitter_profile.get_follow_request(user.profile)
        except ObjectDoesNotExist:
            follow_request_reverse = None

        if follow_request_reverse:
            emitter_profile.remove_received_follow_request(user.profile)  # Eliminar peticion follow (profile -> user)

        # Ver si seguimos al perfil que vamos a bloquear
        try:
            is_follower = user.profile.is_follower(emitter_profile)
        except ObjectDoesNotExist:
            is_follower = None

        if is_follower:
            emitter_profile.remove_relationship(user.profile, 1)  # Eliminar relacion follow
            user.profile.remove_relationship(emitter_profile, 2)  # Eliminar relacion follower

        created = user.profile.add_block(emitter_profile)  # Añadir profile a lista de bloqueados
        created.save()
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

    context = {'user_profile': user}

    if request.method == 'POST':
        response = "success"
        # Procesar temas escritos por el usuario
        tags = request.POST.getlist('tags[]')
        for tag in tags:
            if tag.isspace():
                response = "with_spaces"
                return HttpResponse(json.dumps(response), content_type='application/json')
            user.profile.tags.add(tag)
        # Procesar temas por defecto
        choices = request.POST.getlist('choices[]')
        if not tags and not choices:
            response = "empty"
            return HttpResponse(json.dumps(response), content_type='application/json')
        for choice in choices:
            value = dict(ThemesForm.CHOICES).get(choice)
            user.profile.tags.add(value)
        user.profile.save()
        return HttpResponse(json.dumps(response), content_type='application/json')
    else:
        most_common = UserProfile.tags.most_common()[:10]
        context['top_tags'] = most_common
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


# TODO: que el usuario tenga tags establecidos antes de mostrar las recomendaciones
class RecommendationUsers(ListView):
    """
        Lista de usuarios recomendados segun
        los intereses del usuario.
    """
    model = User
    template_name = "account/reccomendation_after_login.html"

    def get_queryset(self):
        user = self.request.user
        if not user.profile.tags:
            return UserProfile.objects.filter(privacity=UserProfile.ALL).order_by('?')[:20]
        related_items = TaggedItem.objects.none().order_by('count')
        current_item = UserProfile.objects.get(user=user)
        for tag in current_item.tags.all():
            related_items |= tag.taggit_taggeditem_items.all()
        ids = related_items.values_list('object_id', flat=True)
        users = UserProfile.objects.filter(id__in=ids).exclude(user=user)
        if not users:
            users = UserProfile.objects.filter(privacity=UserProfile.ALL).order_by('?').exclude(user=user)[:20]
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
    model = UserProfile
    template_name = "account/like_list.html"
    context_object_name = "object_list"
    page_template = "account/like_entries.html"

    def get_queryset(self):
        username = self.kwargs['username']
        user_profile = get_object_or_404(UserProfile, user__username__iexact=username)
        return user_profile.get_likes_to_me().values('from_like__user__username', 'from_like__user__first_name',
                                                     'from_like__user__last_name', 'from_like__backImage')

    def get_context_data(self, **kwargs):
        context = super(LikeListUsers, self).get_context_data(**kwargs)
        context['user_profile'] = self.kwargs['username']
        user = self.request.user
        self_initial = {'author': user.pk, 'board_owner': user.pk}
        context['publicationSelfForm'] = PublicationForm(initial=self_initial)
        context['searchForm'] = SearchForm()

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
    Busqueda de usuarios por AJAX
    """
    user = request.user

    if user.is_authenticated() and request.is_ajax():
        value = request.GET.get('value', None)

        query = User.objects.filter(~Q(profile__privacity='N') & (Q(username__icontains=value) | Q(first_name__icontains=value) | Q(last_name__icontains=value)))[:20]
        result = []
        for user in query:
            user_json = {}
            user_json['username'] = user.username
            user_json['first_name'] = user.first_name
            user_json['last_name'] = user.last_name
            user_json['avatar'] = get_author_avatar(user)
            result.append(user_json)

        return JsonResponse({'result': result})