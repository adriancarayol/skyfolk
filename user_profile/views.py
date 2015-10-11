from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404, render
from django.template import RequestContext, loader
from user_profile.forms import SearchForm
from publications.forms import PublicationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db.models import Q
from user_profile.forms import ProfileForm, UserForm
from user_profile.models import Relationship, LikeProfile, UserProfile
from publications.models import Publication
from timeline.models import Timeline
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
import json
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.safestring import mark_safe
# allauth
from allauth.account.views import PasswordChangeView
import random


# Create your views here.
@login_required(login_url='accounts/login')
def profile_view(request, username):
    user = request.user
    # para mostarar el cuadro de busqueda en la pagina:
    searchForm = SearchForm(request.POST)

    user_profile = get_object_or_404(
        get_user_model(), username__iexact=username)

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
                print(str(item.pk) + " " + item.user.username + " " + item.user.email)
                requestsToMe_result.append(
                    {'id_profile': item.pk, 'username': item.user.username, })

            # print requestsToMe_result
            json_requestsToMe = json.dumps(requestsToMe_result)

    # saber si el usuario que visita el perfil es amigo
    if request.user.username != username:
        isFriend = True
        try:
            request.user.profile.is_friend(user_profile.profile)
        except ObjectDoesNotExist:
            isFriend = False
    else:
        isFriend = False

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
        friends = user_profile.profile.get_friends()
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

    # cargar recomendaciones por amigos

    listR = []
    try:
        friends = user_profile.profile.get_friends()
        for i in friends:
            try:
                user_i = get_object_or_404(
                    get_user_model(), username__iexact=i["user__username"])
                listR = user_i.profile.get_friends()
            except ObjectDoesNotExist:
                listR = User.objects.all()

    except ObjectDoesNotExist:
        listR = User.objects.all()[:random.randint(1, 10)]



    # mostrar color segun estado (parte emocional)
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

    myList = ['trabajando', 'no', 'si', 'feliz']
    if statusAux != None:
        if compList(statusAux, myList):
            print('>>>>>>>>>>>>>>>>>>>>>>>>' + user_profile.profile.status)
    # mostrar formulario para enviar comentarios/publicaciones
    publicationForm = PublicationForm()

    # cargar lista comentarios
    try:
        publications = user_profile.profile.get_publicationsToMe()
        print('>>>>>>> LISTA PUBLICACIONES: ')
        # print publications
        print(publications)
    except ObjectDoesNotExist:
        publications = None

    publications_top15 = None
    if publications != None:
        if len(publications) > 15:
            request.session['publications_list'] = json.dumps(
                list(publications), cls=DjangoJSONEncoder)
            publications_top15 = publications[0:15]
        else:
            publications_top15 = publications
    # cargar timeline
    print('>>>>>>>>>>> TIMELINE <<<<<<<<<<<')
    try:
        t = Timeline.objects.all()
    except ObjectDoesNotExist:
        t =  None
    # print ">>>>> PERFIL: " + str(user_profile.profile.pk)
    # print ">>>>> VISITANTE/USUARIO: " + str(user.profile.pk)
    return render_to_response('account/profile.html',
                              {'publications_top15': publications_top15, 'listR': listR, 'friends_top12': friends_top12,
                               'user_profile': user_profile, 'searchForm': searchForm,
                               'publicationForm': publicationForm, 'liked': liked, 'n_likes': n_likes, 't': t,
                               'isFriend': isFriend, 'existFriendRequest': existFriendRequest,
                               'json_requestsToMe': json_requestsToMe}, context_instance=RequestContext(request))


@login_required(login_url='accounts/login')
def search(request):
    # para mostarar tambien el cuadro de busqueda en la pagina

    searchForm = SearchForm(request.POST)

    if request.method == 'POST':
        if searchForm.is_valid:
            texto_to_search = request.POST['searchText']
            # hacer busqueda si hay texto para buscar, mediante consulta a la
            # base de datos y pasar el resultado
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
                return render_to_response('account/search.html', {'showPerfilButtons': True, 'searchForm': searchForm,
                                                                  'resultSearch': resultSearch},
                                          context_instance=RequestContext(request))

    else:
        return render_to_response('account/search.html',
                                  {'showPerfilButtons': True, 'searchForm': searchForm, 'resultSearch': ()},
                                  context_instance=RequestContext(request))


@login_required(login_url='/')
def config_changepass(request):
    searchForm = SearchForm(request.POST)
    return render_to_response('account/cf-changepass.html', {'showPerfilButtons': True, 'searchForm': searchForm},
                              context_instance=RequestContext(request))


@login_required(login_url='/')
def config_privacity(request):
    return render_to_response('account/cf-privacity.html', {'showPerfilButtons': True},
                              context_instance=RequestContext(request))


@login_required(login_url='/')
def config_profile(request):
    user_profile = request.user

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
                               'user_form': user_form, 'perfil_form': perfil_form},
                              context_instance=RequestContext(request))
    # return render_to_response('account/cf-profile.html',
    # {'showPerfilButtons':True,'searchForm':searchForm,
    # 'user_form':user_form}, context_instance=RequestContext(request))


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


def request_friend(request):
    print('>>>>>>> peticion amistad ')
    response = "null"
    if request.method == 'POST':
        user = request.user
        slug = request.POST.get('slug', None)
        profileUserId = slug
        print(str(profileUserId))
        try:
            user_friend = user.profile.is_friend(profileUserId)
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
                created = user.profile.add_friend_request(
                    UserProfile.objects.get(pk=slug))
                created.save()

        print(response)

    return HttpResponse(json.dumps(response), content_type='application/javascript')


def respond_friend_request(request):
    response = "null"
    if request.method == 'POST':
        user = request.user
        profileUserId = request.POST.get('slug', None)
        request_status = request.POST.get('status', None)

        try:
            emitter_profile = UserProfile.objects.get(pk=profileUserId)
        except ObjectDoesNotExist:
            emitter_profile = None

        if emitter_profile:
            # user.profile.get_received_friends_requests().delete()
            user.profile.remove_received_friend_request(emitter_profile)

            if request_status == 'accept':

                response = "not_added_friend"
                try:
                    user_friend = user.profile.is_friend(profileUserId)
                except ObjectDoesNotExist:
                    user_friend = None

                if not user_friend:
                    created = user.profile.add_friend(emitter_profile)
                    created.save()
                    response = "added_friend"

            else:
                response = "rejected"

    return HttpResponse(json.dumps(response), content_type='application/javascript')


@login_required(login_url='/')
def friends(request):
    searchForm = SearchForm()

        # cargar lista de amigos (12 primeros)
    try:
        # friends_4 = request.user.profile.get_friends_next4(1)
        friends = request.user.profile.get_friends()
        print('>>>>> Usuario realiza la peticion')
        print(request.user.username)
        print('>>>>>>> LISTA: ')
        print(friends)
        name = request.user.username
    except ObjectDoesNotExist:
        friends = None

    friends_top4 = None
    if friends != None:
        if len(friends) > 12:
            # request.session['friends_list'] = json.dumps(friends.values())
            # request.session['friends_list'] = list(friends)
            # request.session['friends_list'] = serializers.serialize('json', list(friends))
            request.session['friends_list'] = json.dumps(list(friends))
            friends_top4 = friends[0:12]

        else:
            friends_top4 = friends

    return render_to_response('account/amigos.html', {'friends_top4': friends_top4, 'searchForm': searchForm},
                              context_instance=RequestContext(request))


def load_friends(request):
    print('>>>>>> PETICION AJAX, CARGAR MAS AMIGOS')
    friendslist = request.session.get('friends_list', None)
    if friendslist == None:
        friends_next = None
    else:
        friendslist = json.loads(friendslist)
        if request.method == 'POST':
            slug = request.POST.get('slug', None)
            print('>>>>>>> SLUG: ' + slug)
            n = int(slug) * 12
            # devolvera None si esta fuera de rango?
            friends_next = friendslist[n - 12:n]
            print('>>>>>>> LISTA: ')
            print(friends_next)

    return HttpResponse(json.dumps(list(friends_next)), content_type='application/json')


class CustomPasswordChangeView(PasswordChangeView):
    @property
    def success_url(self):
        return '/accounts/password/change/confirmation/'


custom_password_change = login_required(CustomPasswordChangeView.as_view())


def changepass_confirmation(request):
    return render_to_response('account/confirmation_changepass.html', context_instance=RequestContext(request))
