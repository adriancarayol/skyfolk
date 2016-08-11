import json

from allauth.account.views import PasswordChangeView, EmailView
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from notifications.models import Notification
from notifications.signals import notify
from publications.forms import PublicationForm, ReplyPublicationForm
from publications.models import Publication
from timeline.models import Timeline
from user_profile.forms import ProfileForm, UserForm, SearchForm, PrivacityForm, DeactivateUserForm
from user_profile.models import UserProfile


# allauth
# Create your views here.
@login_required(login_url='accounts/login')
def profile_view(request, username):
    user = request.user
    # para mostarar el cuadro de busqueda en la pagina:
    searchForm = SearchForm(request.POST)
    # <<<<<<< HEAD
    #    user_profile = get_object_or_404(
    #        get_user_model(), username__iexact=username)
    # =======

    # username es el nombre del perfil visitado, si coincide con user.username
    # entonces estamos ante el perfil del usuario logueado.
    user_profile = get_object_or_404(get_user_model(),
                                     username__iexact=username)
    # >>>>>>> issue#11
    privacity = user_profile.profile.privacity
    print('ESTADO DE LA CUENTA: ' + str(user.is_active))
    # print(user.email)
    # print('Privacidad del usuario: ' + username + " id: " + str(user_profile.pk) + " " + privacity)
    json_requestsToMe = None
    # saber si el usuario que visita el perfil le gusta
    if request.user.username != username:
        liked = True
        try:
            '''LikeProfile.objects.get(from_like=request.user.profile.id,
            to_like=user_profile.profile)'''
            request.user.profile.has_like(user_profile.profile)
        except ObjectDoesNotExist:
            liked = False
    else:
        liked = False
        requestsToMe = user.profile.get_received_friends_requests()

        if requestsToMe:
            requestsToMe_result = list()
            for item in requestsToMe:
                print(item)
                print(str(item.pk) + " " +
                      item.user.username + " " +
                      item.user.email)
                requestsToMe_result.append(
                    {'id_profile': item.pk, 'username': item.user.username,})

            # print requestsToMe_result
            json_requestsToMe = json.dumps(requestsToMe_result)

    print('LIKED? ' + str(liked))

    # saber si sigo al perfil que visito
    if request.user.username != username:
        isFriend = False
        try:
            if request.user.profile.is_follow(user_profile.profile):
                isFriend = True
        except ObjectDoesNotExist:
            isFriend = False
    else:
        isFriend = False

    # saber si el perfil que visito me sigue

    if request.user.username != username:
        isFollower = False
        try:
            if request.user.profile.is_follower(user_profile.profile):
                isFollower = True
        except ObjectDoesNotExist:
            isFollower = False
    else:
        isFollower = False

    # saber si el perfil que visito esta bloqueado
    if request.user.username != username:
        isBlocked = False
        try:
            if request.user.profile.is_blocked(user_profile.profile):
                isBlocked = True
        except ObjectDoesNotExist:
            isBlocked = False
    else:
        isBlocked = False

    print('IS BLOCKED? ' + str(isBlocked))
    # number of likes to him
    n_likes = len(user_profile.profile.likesToMe.all())

    try:
        friend_request = user.profile.get_follow_request(user_profile.profile)
    except ObjectDoesNotExist:
        friend_request = None

    if friend_request:
        existFollowRequest = True
        print('Exist follow request? ' + str(True))
    else:
        existFollowRequest = False
        print('Exist follow request? ' + str(False))

    # cargar lista de amigos (12 primeros)
    try:
        # friends_4 = request.user.profile.get_friends_next4(1)
        friends = user_profile.profile.get_following()
        print('>>>>>>> LISTA: ')
        print(friends)
    except ObjectDoesNotExist:
        friends = None

    friends_top12 = None
    if friends != None:
        if len(friends) > 12:
            request.session['friends_list'] = json.dumps(list(friends))
            friends_top12 = friends[0:12]

        else:
            friends_top12 = friends

    # obtener num de seguidores
    try:
        followers = user_profile.profile.get_followers().count()
    except ObjectDoesNotExist:
        followers = None
    # obtener num de seguidos
    try:
        following = user_profile.profile.get_following().count()
    except ObjectDoesNotExist:
        following = None

    # cargar recomendaciones por amigos
    # TODO
    listR = []
    '''
    try:
        friends = request.user.profile.get_friends()
        if len(friends) < 10:
            print("El usuario tiene menos de 10 amigos")
            listR = User.objects.all()
        else:
            print("El usuario tiene mas o igual a 10 amigos")
            listR = friends
        print("Obteniendo recomendaciones del usuario" + request.user.username)
    except ObjectDoesNotExist:
        friends = None
        print("El usuario no tiene amigos")
    '''
    # TODO
    # Parte emocional - Según el estado, mostrar color, etcétera.
    '''
    try:
        statusAux = user_profile.profile.status.lower().split()
    except:
        statusAux = None

    def compList(list1, list2):
        for i in list1:
            if i in list2:
                return True
            else:
                return False

    estados = {'feliz': 1, 'triste': 2, 'cabreado': 3, 'enojado': 4, 'sorprendido': 5,
               'somnoliento': 6, 'cansado': 7, 'pensativo': 8, 'saludable': 9,
               'enfermo': 10, 'hambriento': 11, 'asustado': 12, 'aburrido': 13, 'apenado': 14}

    if statusAux != None:
        if compList(statusAux, estados):
            print('>>>>>>>>>>>>>>>>>>>>>>>>' + user_profile.profile.status)
        else:
            print('>>> El usuario ' + user_profile.username + " no tiene ningún estado ańimico")
    '''
    # mostrar formulario para enviar comentarios/publicaciones
    initial = {'author': user.pk, 'board_owner': user_profile.pk}
    publicationForm = PublicationForm(initial=initial)
    reply_pub_form = ReplyPublicationForm(initial=initial)

    # cargar lista comentarios
    try:
        # publications = Publication.objects.get_authors_publications(
        #                                             author_pk=user_profile.pk)
        if isFriend:
            publications = Publication.objects.get_friend_profile_publications(
                user_pk=user.pk,
                board_owner_pk=user_profile.pk)
        else:
            publications = Publication.objects.get_user_profile_publications(
                user_pk=user.pk,
                board_owner_pk=user_profile.pk)
        print('>>>>>>> LISTA PUBLICACIONES: ')
        # print publications
        print(publications)
    except ObjectDoesNotExist:
        publications = None

    publications_top15 = None
    if publications:
        if len(publications) > 15:
            # request.session['publications_list'] = \
            #                       serializers.serialize('json', publications)
            publications_top15 = publications[0:15]
        else:
            publications_top15 = publications

    print('>>>>>>> LISTA PUBLICACIONES TOP 15: ')
    # print publications
    print(publications)

    # cargar timeline
    print('>>>>>>>>>>> TIMELINE <<<<<<<<<<<')
    print('views.py line:164 publications_top {}'.format(publications_top15))
    try:
        timeline = user_profile.profile.getTimelineToMe()
    except ObjectDoesNotExist:
        timeline = None

    return render_to_response('account/profile.html', {
        'publications_top15': publications_top15,
        'listR': listR, 'friends_top12': friends_top12,
        'user_profile': user_profile,
        'searchForm': searchForm,
        'publicationForm': publicationForm,
        'reply_publication_form': reply_pub_form,
        'liked': liked, 'n_likes': n_likes,
        'timeline': timeline, 'isFriend': isFriend,
        'existFollowRequest': existFollowRequest,
        'json_requestsToMe': json_requestsToMe,
        'followers': followers,
        'privacity': privacity,
        'isFollower': isFollower,
        'following': following,
        'isBlocked': isBlocked},
                              context_instance=RequestContext(request))


# >>>>>>> issue#11


@login_required(login_url='accounts/login')
def search(request):
    # para mostarar tambien el cuadro de busqueda en la pagina
    searchForm = SearchForm(request.POST)
    # mostrar formulario para enviar comentarios/publicaciones
    publicationForm = PublicationForm()

    if request.method == 'POST':
        if searchForm.is_valid:
            result_messages = None
            texto_to_search = request.POST['searchText']
            # hacer busqueda si hay texto para buscar, mediante consulta a la
            # base de datos y pasar el resultado
            if texto_to_search:
                words = texto_to_search.split()
                if len(words) == 1:
                    resultSearch = User.objects.filter(Q(first_name__icontains=texto_to_search) | Q(
                        last_name__icontains=texto_to_search) | Q(username__icontains=texto_to_search), is_active=True)

                elif len(words) == 2:
                    resultSearch = User.objects.filter(
                        first_name__icontains=words[0], last_name__icontains=words[1], is_active=True)
                else:
                    resultSearch = User.objects.filter(
                        first_name__icontains=words[0], last_name__icontains=words[1] + ' ' + words[2], is_active=True)
                # usamos la expresion regular para descartar las imagenes de los comentarios
                for w in words:
                    result_messages = Publication.objects.filter(
                        Q(content__iregex=r"\b%s\b" % w) & ~Q(content__iregex=r'<img[^>]+src="([^">]+)"') |
                        Q(author__username__icontains=w) |
                        Q(author__first_name__icontains=w) |
                        Q(author__last_name__icontains=w), author__is_active=True).order_by('content').order_by(
                        'created').reverse()  # or .order_by('created').reverse()

                return render_to_response('account/search.html', {'showPerfilButtons': True, 'searchForm': searchForm,
                                                                  'resultSearch': resultSearch,
                                                                  'resultMessages': result_messages,
                                                                  'words': words},
                                          context_instance=RequestContext(request))

    else:
        return render_to_response('account/search.html',
                                  {'showPerfilButtons': True, 'searchForm': searchForm, 'resultSearch': (
                                  ), 'publicationForm': publicationForm},
                                  context_instance=RequestContext(request))


# TODO
class AdvancedView(TemplateView):
    template_name = "account/search-avanzed.html"

    def get(self, request, *args, **kwargs):
        publicationForm = PublicationForm()
        searchForm = SearchForm(request.POST)

        return render_to_response(self.template_name,
                                  {'publicationForm': publicationForm,
                                   'searchForm': searchForm},
                                  context_instance=RequestContext(request))


advanced_view = login_required(AdvancedView.as_view())


@login_required(login_url='/')
def config_privacity(request):
    publicationForm = PublicationForm()
    searchForm = SearchForm()
    print('>>>>> PETICION CONFIG')
    if request.POST:
        print('>>>> PASO 1')
        privacity_form = PrivacityForm(data=request.POST, instance=request.user.profile)
        print('>>>> PASO 1.1')
        if privacity_form.is_valid():
            print('>>>>> SAVE')
            privacity_form.save()
            return HttpResponseRedirect('/config/privacity')
    else:
        privacity_form = PrivacityForm(instance=request.user.profile)
        print('PASO ULTIMO')
    return render_to_response('account/cf-privacity.html',
                              {'showPerfilButtons': True, 'searchForm': searchForm, 'publicationForm': publicationForm,
                               'privacity_form': privacity_form},
                              context_instance=RequestContext(request))


@login_required(login_url='/')
def config_profile(request):
    user_profile = request.user
    publicationForm = PublicationForm()
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
    return render_to_response('account/cf-profile.html',
                              {'showPerfilButtons': True, 'searchForm': searchForm, 'user_profile': user_profile,
                               'user_form': user_form, 'perfil_form': perfil_form, 'publicationForm': publicationForm},
                              context_instance=RequestContext(request))
    # return render_to_response('account/cf-profile.html',
    # {'showPerfilButtons':True,'searchForm':searchForm,
    # 'user_form':user_form}, context_instance=RequestContext(request))


@login_required(login_url='/')
def config_pincode(request):
    pin = request.user.profile.pin
    publicationForm = PublicationForm()
    searchForm = SearchForm()

    return render_to_response('account/cf-pincode.html', {'showPerfilButtons': True, 'searchForm': searchForm,
                                                          'publicationForm': publicationForm, 'pin': pin},
                              context_instance=RequestContext(request))


@login_required(login_url='/')
def config_blocked(request):
    list_blocked = request.user.profile.get_blockeds()
    publicationForm = PublicationForm()
    searchForm = SearchForm()

    return render_to_response('account/cf-blocked.html', {'showPerfilButtons': True, 'searchForm': searchForm,
                                                          'publicationForm': publicationForm, 'blocked': list_blocked},
                              context_instance=RequestContext(request))


@login_required(login_url='accounts/login')
def add_friend_by_username_or_pin(request):
    print('ADD FRIEND BY USERNAME OR PIN')
    response = 'no_added_friend'
    if request.method == 'POST':
        if request.POST.get('tipo') == 'pin':
            print('STEP 1')
            user_request = request.user
            pin = request.POST.get('valor')
            user = user_request.profile
            print('STEP 2')
            if user.pin == pin:
                return HttpResponse(json.dumps('your_own_pin'), content_type='application/javascript')

            try:
                friend_pk = UserProfile.get_pk_for_pin(pin)
                friend = UserProfile.objects.get(pk=friend_pk)
            except:
                return HttpResponse(json.dumps('no_match'), content_type='application/javascript')

            if user.is_follow(friend):
                return HttpResponse(json.dumps('its_your_friend'), content_type='application/javascript')
            # Me tienen bloqueado
            try:
                is_blocked = friend.is_blocked(user)
            except ObjectDoesNotExist:
                is_blocked = None
            if is_blocked:
                response = "user_blocked"
                return HttpResponse(json.dumps(response), content_type='application/javascript')
            # Yo tengo bloqueado al perfil
            try:
                blocked_profile = user.is_blocked(friend)
            except ObjectDoesNotExist:
                blocked_profile = None
            if blocked_profile:
                response = "blocked_profile"
                return HttpResponse(json.dumps(response), content_type='application/javascript')
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
                try:
                    notification = notification[0][1]
                except IndexError:
                    notification = None
                # Enlazamos notificacion con peticion de amistad
                try:
                    created = user.add_follow_request(
                        friend, notification)
                    created.save()
                    response = 'new_petition'
                except ObjectDoesNotExist:
                    response = "no_added_friend"



        else:  # tipo == username
            user_request = request.user
            username = request.POST.get('valor')
            user = user_request.profile

            if user.user.username == username:
                return HttpResponse(json.dumps('your_own_username'), content_type='application/javascript')

            friend = None
            try:
                friend = UserProfile.objects.get(user__username=username)
            except ObjectDoesNotExist:
                return HttpResponse(json.dumps('no_match'), content_type='application/javascript')

            if user.is_follow(friend):  # if user.is_friend(friend):
                return HttpResponse(json.dumps('its_your_friend'), content_type='application/javascript')

            # Me tienen bloqueado
            try:
                is_blocked = friend.is_blocked(user)
            except ObjectDoesNotExist:
                is_blocked = None
            if is_blocked:
                response = "user_blocked"
                return HttpResponse(json.dumps(response), content_type='application/javascript')
            # Yo tengo bloqueado al perfil
            try:
                blocked_profile = user.is_blocked(friend)
            except ObjectDoesNotExist:
                blocked_profile = None
            if blocked_profile:
                response = "blocked_profile"
                return HttpResponse(json.dumps(response), content_type='application/javascript')

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
                try:
                    notification = notification[0][1]
                except IndexError:
                    notification = None
                # Enlazamos notificacion y peticion de amistad
                try:
                    created = user.add_follow_request(
                        friend, notification)
                    created.save()
                    response = 'new_petition'
                except ObjectDoesNotExist:
                    response = "no_added_friend"

    return HttpResponse(json.dumps(response), content_type='application/javascript')


@login_required(login_url='/')
def like_profile(request):
    response = "null"
    if request.method == 'POST':
        user = request.user
        slug = request.POST.get('slug', None)
        actual_profile = UserProfile.objects.get(pk=slug)

        try:
            user_liked = user.profile.has_like(actual_profile)
        except ObjectDoesNotExist:
            user_liked = None

        if user_liked:
            user_liked.delete()
            response = "nolike"
        else:
            print(str(slug))
            created = user.profile.add_like(actual_profile)
            created.save()
            response = "like"
    print('%s da like a %s' % (user.username, actual_profile.user.username))
    print("Response: " + response)
    return HttpResponse(json.dumps(response), content_type='application/javascript')


# Request follow
@login_required(login_url='accounts/login')
def request_friend(request):
    print('>>>>>>> peticion amistad ')
    response = "null"
    if request.method == 'POST':
        user = request.user
        slug = request.POST.get('slug', None)
        profile = UserProfile.objects.get(pk=slug)
        try:
            is_blocked = profile.is_blocked(user.profile)
        except ObjectDoesNotExist:
            is_blocked = None
        if is_blocked:
            response = "user_blocked"
            return HttpResponse(json.dumps(response), content_type='application/javascript')

        try:
            #  user_friend = user.profile.is_friend(profileUserId)
            user_friend = user.profile.is_follow(profile)  # Comprobamos si YO ya sigo al perfil deseado.
        except ObjectDoesNotExist:
            user_friend = None

        if user_friend:
            response = "isfriend"
        else:
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
                try:
                    notification = notification[0][1]
                except IndexError:
                    notification = None
                # Enlazamos notificacion con peticion de amistad
                try:
                    created = user.profile.add_follow_request(
                        profile, notification)
                    created.save()
                except ObjectDoesNotExist:
                    response = "no_added_friend"

        print(response)

    return HttpResponse(json.dumps(response), content_type='application/javascript')


# Responde request follow
@login_required(login_url='/')
def respond_friend_request(request):
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
            # user.profile.get_received_friends_requests().delete()
            user.profile.remove_received_follow_request(emitter_profile)

            if request_status == 'accept':
                response = "not_added_friend"
                try:
                    #  user_friend = user.profile.is_friend(profileUserId)
                    user_friend = user.profile.is_follower(profileUserId)
                except ObjectDoesNotExist:
                    user_friend = None

                if not user_friend:
                    #  created = user.profile.add_friend(emitter_profile)
                    created = user.profile.add_follower(
                        emitter_profile)  # Me añado como seguidor del perfil que quiero seguir
                    created_2 = emitter_profile.add_follow(
                        user.profile)  # Añado a mi lista de "seguidos" al peril que quiero seguir
                    created.save()
                    created_2.save()

                    t, created = Timeline.objects.get_or_create(author=user.profile, profile=emitter_profile,
                                                                verb='¡<a href="/profile/%s">%s</a> ahora sigue a <a href="/profile/%s">%s</a>!' % (
                                                                    emitter_profile.user.username,
                                                                    emitter_profile.user.username, user.username,
                                                                    user.username),
                                                                type='new_relation')
                    t_, created_ = Timeline.objects.get_or_create(author=emitter_profile, profile=user.profile,
                                                                  verb='¡<a href="/profile/%s">%s</a> tiene un nuevo seguidor, <a href="/profile/%s">%s</a>!' % (
                                                                      user.username, user.username,
                                                                      emitter_profile.user.username,
                                                                      emitter_profile.user.username),
                                                                  type='new_relation')

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
    print('>>>>>> PETICION AJAX, CARGAR MAS AMIGOS')
    friendslist = request.user.profile.get_followers()

    if friendslist == None:
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


@login_required(login_url='/')
def followers(request, username):
    searchForm = SearchForm()
    publicationForm = PublicationForm()
    user_profile = get_object_or_404(
        get_user_model(), username__iexact=username)

    try:
        friends = user_profile.profile.get_followers()
    except ObjectDoesNotExist:
        friends = None

    if (len(friends) > 12):
        friends_top4 = friends[0:12]
    else:
        friends_top4 = friends
    return render_to_response('account/followers.html',
                              {'friends_top4': friends_top4, 'searchForm': searchForm,
                               'publicationForm': publicationForm},
                              context_instance=RequestContext(request))


@login_required(login_url='/')
def following(request, username):
    searchForm = SearchForm()
    publicationForm = PublicationForm()
    user_profile = get_object_or_404(
        get_user_model(), username__iexact=username)

    try:
        friends = user_profile.profile.get_following()
    except ObjectDoesNotExist:
        friends = None

    if len(friends) > 12:
        friends_top4 = friends[0:12]
    else:
        friends_top4 = friends
    return render_to_response('account/amigos.html', {'friends_top4': friends_top4, 'searchForm': searchForm,
                                                      'publicationForm': publicationForm},
                              context_instance=RequestContext(request))


# Load follows
@login_required(login_url='/')
def load_follows(request):
    print('>>>>>> PETICION AJAX, CARGAR MAS AMIGOS')
    friendslist = request.user.profile.get_following()

    if friendslist == None:
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
    publicationForm = PublicationForm()
    searchForm = SearchForm()

    def get(self, request, *args, **kwargs):
        context = locals()
        context['publicationForm'] = self.publicationForm
        context['searchForm'] = self.searchForm
        context['showPerfilButtons'] = True

        return render_to_response(self.template_name, context, context_instance=RequestContext(request))


password_done = login_required(PassWordChangeDone.as_view())


# Modificacion del formulario para cambiar contraseña
class CustomPasswordChangeView(PasswordChangeView):
    success_url = reverse_lazy("account_done_password")
    publicationForm = PublicationForm()
    searchForm = SearchForm()

    def get_context_data(self, **kwargs):
        ret = super(PasswordChangeView, self).get_context_data(**kwargs)
        # NOTE: For backwards compatibility
        ret['password_change_form'] = ret.get('form')
        ret['publicationForm'] = self.publicationForm
        ret['searchForm'] = self.searchForm
        ret['showPerfilButtons'] = True
        # (end NOTE)
        return ret


custom_password_change = login_required(CustomPasswordChangeView.as_view())


# Modificacion del formulario para manejar los emails
class CustomEmailView(EmailView):
    publicationForm = PublicationForm()
    searchForm = SearchForm()

    def get_context_data(self, **kwargs):
        ret = super(EmailView, self).get_context_data(**kwargs)
        # NOTE: For backwards compatibility
        ret['add_email_form'] = ret.get('form')
        ret['publicationForm'] = self.publicationForm
        ret['searchForm'] = self.searchForm
        ret['showPerfilButtons'] = True
        # (end NOTE)
        return ret


custom_email = login_required(CustomEmailView.as_view())


@login_required(login_url='/')
def changepass_confirmation(request):
    return render_to_response('account/confirmation_changepass.html', context_instance=RequestContext(request))


# Modificacion del template para desactivar una cuenta
class DeactivateAccount(FormView):
    template_name = 'account/account_inactive.html'
    form_class = DeactivateUserForm
    success_url = reverse_lazy('account_logout')

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['form'] = self.form_class
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = self.get_form(self.form_class)
        user = request.user

        if user.is_authenticated():
            if form.is_valid():
                user.is_active = form.clean_is_active()
                if user.is_active:
                    return self.form_valid(form=form, **kwargs)
                else:
                    user.delete()
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

class GalleryTemplate(TemplateView):
    template_name = "account/photo_gallery.html"
    publicationForm = PublicationForm()
    searchForm = SearchForm()

    def get(self, request, *args, **kwargs):
        return render_to_response(self.template_name,
                                  {'publicationForm': self.publicationForm,
                                   'searchForm': self.searchForm},
                                  context_instance=RequestContext(request))

user_gallery = login_required(GalleryTemplate.as_view())

def bloq_user(request):
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


def welcomeView(request, username):
    newUser = username
    return render_to_response('account/nuevosusuarios.html',
                              context_instance=RequestContext(request, {'newUser': newUser}))


def welcomeStep1(request, username):
    newUser = request.user.username
    return render_to_response('account/welcomestep1.html',
                              context_instance=RequestContext(request, {'newUser': newUser}))


def setfirstLogin(request):
    response = False
    if request.method == 'POST':
        username = request.POST.get('username', None)
        response = True

    return HttpResponse(json.dumps(response), content_type='application/json')
