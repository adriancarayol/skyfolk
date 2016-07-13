import json

from allauth.account.views import PasswordChangeView
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
# from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from publications.forms import PublicationForm, ReplyPublicationForm
from publications.models import Publication
from user_profile.forms import ProfileForm, UserForm, SearchForm, PrivacityForm
from user_profile.models import UserProfile
from notifications.signals import notify

# allauth
# Create your views here.
@login_required(login_url='accounts/login')
def profile_view(request, username):
    user = request.user
    # para mostarar el cuadro de busqueda en la pagina:
    searchForm = SearchForm(request.POST)
#<<<<<<< HEAD
#    user_profile = get_object_or_404(
#        get_user_model(), username__iexact=username)
#=======

    # username es el nombre del perfil visitado, si coincide con user.username
    # entonces estamos ante el perfil del usuario logueado.
    user_profile = get_object_or_404(get_user_model(),
                                     username__iexact=username)
#>>>>>>> issue#11
    privacity = user_profile.profile.get_privacity()

    # print(user.email)
    print('Privacidad del usuario: ' + username + " id: " + str(user_profile.pk) + " " + user_profile.profile.privacity)
    json_requestsToMe = None
    # saber si el usuario que visita el perfil le gusta
    if request.user.username != username:
        liked = True
        try:
            # LikeProfile.objects.get(from_like=request.user.profile.id, to_like=user_profile.profile)
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
                print(
                    str(item.pk) + " " + item.user.username + " " + item.user.email)
                requestsToMe_result.append(
                    {'id_profile': item.pk, 'username': item.user.username,})

            # print requestsToMe_result
            json_requestsToMe = json.dumps(requestsToMe_result)

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

    # number of likes to him
    n_likes = len(user_profile.profile.likesToMe.all())

    try:
        friend_request = user.profile.get_friend_request(user_profile.profile)
    except ObjectDoesNotExist:
        friend_request = None

    if friend_request:
        existFriendRequest = True
        print(True)
    else:
        existFriendRequest = False
        print(False)

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
            # request.session['friends_list'] = json.dumps(friends.values())
            # request.session['friends_list'] = list(friends)
            # request.session['friends_list'] = serializers.serialize('json', list(friends))
            request.session['friends_list'] = json.dumps(list(friends))
            friends_top12 = friends[0:12]

        else:
            friends_top12 = friends

    # obtener lista de seguidores
    try:
        followers = user_profile.profile.get_followers().count()
        print("Num de seguidores: >>>>>>>>>>>>>>>>>>>>" + str(followers))
    except ObjectDoesNotExist:
        followers = None

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

#<<<<<<< HEAD
#    # notificaciones
#    notifications_profile = user.notifications.unread()
#    print(notifications_profile)
#    return render_to_response('account/profile.html',
#                              {'publications_top15': publications_top15, 'listR': listR, 'friends_top12': friends_top12,
#                               'user_profile': user_profile, 'searchForm': searchForm,
#                               'publicationForm': publicationForm, 'liked': liked, 'n_likes': n_likes,
#                               'timeline': timeline,
#                               'isFriend': isFriend, 'existFriendRequest': existFriendRequest,
#                               'json_requestsToMe': json_requestsToMe,
#                               'followers': followers, 'privacity': privacity,
#                               'isFollower': isFollower}, context_instance=RequestContext(request))
#=======
    return render_to_response('account/profile.html', {
                                'publications_top15': publications_top15,
                                'listR': listR, 'friends_top12': friends_top12,
                                'user_profile': user_profile,
                                'searchForm': searchForm,
                                'publicationForm': publicationForm,
                                'reply_publication_form': reply_pub_form,
                                'liked': liked, 'n_likes': n_likes,
                                'timeline': timeline, 'isFriend': isFriend,
                                'existFriendRequest': existFriendRequest,
                                'json_requestsToMe': json_requestsToMe,
                                'followers':followers, 'privacity': privacity,
                                'isFollower': isFollower},
                                context_instance=RequestContext(request)
                              )
#>>>>>>> issue#11


@login_required(login_url='accounts/login')
def search(request):
    # para mostarar tambien el cuadro de busqueda en la pagina

    searchForm = SearchForm(request.POST)
    # mostrar formulario para enviar comentarios/publicaciones
    publicationForm = PublicationForm()

    if request.method == 'POST':
        if searchForm.is_valid:
            texto_to_search = request.POST['searchText']
            # hacer busqueda si hay texto para buscar, mediante consulta a la
            # base de datos y pasar el resultado
            if texto_to_search[0] == '/':
                texto_to_search = texto_to_search[1:]
            if texto_to_search:
                words = texto_to_search.split()
                if len(words) == 1:
                    resultSearch = User.objects.filter(Q(first_name__icontains=texto_to_search) | Q(
                        last_name__icontains=texto_to_search) | Q(username__icontains=texto_to_search))

                elif len(words) == 2:
                    resultSearch = User.objects.filter(
                        first_name__icontains=words[0], last_name__icontains=words[1])
                else:
                    resultSearch = User.objects.filter(
                        first_name__icontains=words[0], last_name__icontains=words[1] + ' ' + words[2])

                for w in words:
                    print('Palabra encontrada -> ' + w)
                    result_messages = Publication.objects.filter(
                        Q(content__iregex=r"\b%s\b" % w) & ~Q(content__iregex=r'<img[^>]+src="([^">]+)"') |
                        Q(author__username__icontains=w) |
                        Q(author__first_name__icontains=w) |
                        Q(author__last_name__icontains=w)).order_by('content').order_by('created').reverse() # or .order_by('created').reverse()

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


'''@login_required(login_url='/')
def config_changepass(request):
    searchForm = SearchForm()
    publicationForm = PublicationForm()
    return render_to_response('account/cf-changepass.html', {'showPerfilButtons': True, 'searchForm': searchForm, 'publicationForm': publicationForm},
                              context_instance=RequestContext(request))


@login_required(login_url='/')
def config_privacity(request):
    searchForm = SearchForm()
    publicationForm = PublicationForm()
    return render_to_response('account/cf-privacity.html', {'showPerfilButtons': True, 'searchForm': searchForm, 'publicationForm': publicationForm},
                              context_instance=RequestContext(request))'''



@login_required(login_url='/')
def config_privacity(request):
    user_profile = request.user
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
    return render_to_response('account/cf-privacity.html', {'showPerfilButtons':True, 'searchForm': searchForm, 'publicationForm': publicationForm, 'privacity_form': privacity_form},
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
    pin = UserProfile.objects.get(pk=request.user.pk).pin
    publicationForm = PublicationForm()
    searchForm = SearchForm()

    return render_to_response('account/cf-pincode.html', {'showPerfilButtons':True, 'searchForm': searchForm,
                                                          'publicationForm': publicationForm, 'pin': pin},
                              context_instance=RequestContext(request))


@login_required(login_url='accounts/login')
def add_friend_by_username_or_pin(request):
    response = 'no_added_friend'
    if request.method == 'POST':
        if request.POST.get('tipo') == 'pin':
            user = request.user
            pin = request.POST.get('valor')
            user = UserProfile.objects.get(pk=user.pk)
            if user.pin == pin:
                return HttpResponse(json.dumps('your_own_pin'), content_type='application/javascript')

            try:
                friend_pk = UserProfile.get_pk_for_pin(pin)
                friend = UserProfile.objects.get(pk=friend_pk)
            except:
                return HttpResponse(json.dumps('no_match'), content_type='application/javascript')

            '''if user.is_friend(friend):
                return HttpResponse(json.dumps('its_your_friend'), content_type='application/javascript')'''
            if user.is_follow(friend):
                return HttpResponse(json.dumps('its_your_friend'), content_type='application/javascript')

        # enviamos peticion de amistad
            try:
                friend_request = user.get_friend_request(
                    UserProfile.objects.get(pk=friend))
                response = 'in_progress'
            except ObjectDoesNotExist:
                friend_request = None

            if not friend_request:
                created = user.add_friend_request(
                    UserProfile.objects.get(pk=friend))
                created.save()

                response = 'new_petition'

            '''
            try:
                #  user.add_friend(friend)
                user.add_follow(friend)  # X añade a Y como "seguido"
                friend.add_follower(user)  # Y añade a X como "seguidor"
                response = 'added_friend'
            except Exception as e:
                print(e)
            '''

        else:  # tipo == username
            user = request.user
            username = request.POST.get('valor')
            user = UserProfile.objects.get(pk=user.pk)

            if user.user.username == username:
                return HttpResponse(json.dumps('your_own_username'), content_type='application/javascript')

            friend = None
            try:
                friend = UserProfile.objects.get(user__username=username)
            except ObjectDoesNotExist:
                return HttpResponse(json.dumps('no_match'), content_type='application/javascript')
            if user.is_follow(friend):  # if user.is_friend(friend):
                return HttpResponse(json.dumps('its_your_friend'), content_type='application/javascript')
            # enviamos peticion de amistad
            try:
                friend_request = user.get_friend_request(
                    UserProfile.objects.get(user__username=username))
                response = 'in_progress'
            except ObjectDoesNotExist:
                friend_request = None

            if not friend_request:
                created = user.add_friend_request(
                    UserProfile.objects.get(user__username=username))
                created.save()
                response = 'new_petition'
                # TODO terminar notificaciones al enviar peticiones de amistad
                notify.send(user, actor=User.objects.get(pk=user.pk).username, recipient=User.objects.get(pk=user.pk),
                            verb=u'¡Nueva peticion de amistad!')

            '''
            try:
                # user.add_friend(friend)
                user.add_follow(friend)  # X añade a Y como "seguido"
                friend.add_follower(user)  # Y añade a X como "seguidor"
                response = 'added_friend'
            except Exception as e:
                print(e)
            '''

    return HttpResponse(json.dumps(response), content_type='application/javascript')


def like_profile(request):
    response = "null"
    if request.method == 'POST':
        user = request.user
        slug = request.POST.get('slug', None)
        profileUserId = slug
        try:
            user_liked = user.profile.has_like(profileUserId)
        except ObjectDoesNotExist:
            user_liked = None

        if user_liked:
            user_liked.delete()
            response = "nolike"
        else:
            print(str(slug))
            created = user.profile.add_like(UserProfile.objects.get(pk=slug))
            created.save()
            response = "like"

    return HttpResponse(json.dumps(response), content_type='application/javascript')


# Request follow
@login_required(login_url='accounts/login')
def request_friend(request):
    print('>>>>>>> peticion amistad ')
    response = "null"
    if request.method == 'POST':
        user = request.user
        slug = request.POST.get('slug', None)
        # print(str(slug)) # slug = profile id
        try:
            #  user_friend = user.profile.is_friend(profileUserId)
            user_friend = user.profile.is_follow(slug)  # Comprobamos si YO ya sigo al perfil deseado.
        except ObjectDoesNotExist:
            user_friend = None

        if user_friend:
            response = "isfriend"
        else:
            response = "inprogress"
            try:
                friend_request = user.profile.get_friend_request(
                    UserProfile.objects.get(pk=slug))
            except ObjectDoesNotExist:
                friend_request = None

            if not friend_request:
                notify.send(user, actor=User.objects.get(pk=user.pk).username,
                            recipient=UserProfile.objects.get(pk=slug).user,
                            verb=u'quiere seguirte.', level='friendrequest')
                created = user.profile.add_friend_request(
                    UserProfile.objects.get(pk=slug))
                created.save()

        print(response)

    return HttpResponse(json.dumps(response), content_type='application/javascript')


# Responde request follow
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
            user.profile.remove_received_friend_request(emitter_profile)

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
                    response = "added_friend"

            else:
                response = "rejected"

    return HttpResponse(json.dumps(response), content_type='application/javascript')

# Elimina relación entre dos usuarios
def remove_relationship(request):
    response = None
    user = request.user
    slug = request.POST.get('slug', None)
    print("REMOVE RELATIONSHIPT SLUG(%s)" % str(slug))
    if request.method == 'POST':
        try:
            user_friend = user.profile.is_follow(slug)  # Comprobamos si YO ya sigo al perfil deseado.
        except ObjectDoesNotExist:
            user_friend = None

        if user_friend:
            user.profile.remove_relationship(slug, 2)
            response = True
        else:
            response = False
    return HttpResponse(json.dumps(response), content_type='application/javascript')

# Load followers
def load_followers(request):
    print('>>>>>> PETICION AJAX, CARGAR MAS AMIGOS')
    friendslist = request.user.profile.get_followers()

    if friendslist == None:
        friends_next = None
    else:
        #friendslist = json.loads(friendslist)
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

    if (len(friends) > 1):
        friends_top4 = friends[0:1]
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

    if len(friends) > 4:
        friends_top4 = friends[0:4]
    else:
        friends_top4 = friends
    return render_to_response('account/amigos.html', {'friends_top4': friends_top4, 'searchForm': searchForm,
                                                      'publicationForm': publicationForm},
                              context_instance=RequestContext(request))

# Load follows
def load_follows(request):
    print('>>>>>> PETICION AJAX, CARGAR MAS AMIGOS')
    friendslist = request.user.profile.get_following()

    if friendslist == None:
        friends_next = None
    else:
        #friendslist = json.loads(friendslist)
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


class CustomPasswordChangeView(PasswordChangeView):
    @property
    def success_url(self):
        return '/accounts/password/change/confirmation/'


custom_password_change = login_required(CustomPasswordChangeView.as_view())


def changepass_confirmation(request):
    return render_to_response('account/confirmation_changepass.html', context_instance=RequestContext(request))


def welcomeView(request, username):
    newUser = username
    return render_to_response("account/nuevosusuarios.html",
                              context_instance=RequestContext(request, {'newUser': newUser}))


def welcomeStep1(request, username):
    newUser = request.user.username
    return render_to_response("account/welcomestep1.html",
                              context_instance=RequestContext(request, {'newUser': newUser}))


def setfirstLogin(request):
    response = False
    if request.method == 'POST':
        username = request.POST.get('username', None)
        response = True

    return HttpResponse(json.dumps(response), content_type='application/json')
