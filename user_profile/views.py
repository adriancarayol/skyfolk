from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response , get_object_or_404, render
from django.template import RequestContext, loader
from user_profile.forms import SearchForm
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db.models import Q
from forms import ProfileForm, UserForm
from user_profile.models import Relationship, LikeProfile, UserProfile
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.utils import simplejson
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.safestring import mark_safe


# Create your views here.
@login_required(login_url='accounts/login')
def profile_view(request, username):

	user = request.user
	#para mostarar el cuadro de busqueda en la pagina:
	searchForm = SearchForm(request.POST)

	user_profile = get_object_or_404(get_user_model(), username__iexact=username)

	requestsToMe = None

	#saber si el usuario que visita el perfil le gusta
	if request.user.username != username:
		liked=True
		try:
			#LikeProfile.objects.get(from_like=request.user.profile.id, to_like=user_profile.profile)
			request.user.profile.has_like(user_profile.profile)
		except ObjectDoesNotExist:
			liked=False
	else:
		liked=False
		requestsToMe = user.profile.get_received_friends_requests()

		requestsToMe_result = list()
		for item in requestsToMe:
			print item
			print str(item.pk) + " " + item.user.username + " " + item.user.email
			#requestsToMe_result = {'id_profile': item.pk,'username': item.user.username,}
			requestsToMe_result.append({'id_profile': item.pk,'username': item.user.username,})    

		print requestsToMe_result

	#saber si el usuario que visita el perfil es amigo
	if request.user.username != username:
		isFriend=True
		try:
			request.user.profile.is_friend(user_profile.profile)
		except ObjectDoesNotExist:
			isFriend=False
	else:
		isFriend=False	


	#number of likes to him
	n_likes = len(user_profile.profile.likesToMe.all())


	try:
		friend_request = user.profile.get_friend_request(user_profile.profile)
	except ObjectDoesNotExist:
		friend_request = None

	if friend_request:
		existFriendRequest = True
		print True
	else:
		existFriendRequest = False
		print False


	#json_requestsToMe = simplejson.dumps(requestsToMe)
	#json_requestsToMe = serializers.serialize('json', requestsToMe_result)
	json_requestsToMe = simplejson.dumps(requestsToMe_result)
	#json_requestsToMe = list(requestsToMe)
	#json_requestsToMe = simplejson.dumps(list(requestsToMe), cls=DjangoJSONEncoder)
	#json_requestsToMe = simplejson.dumps(serializers.serialize('json', requestsToMe))
	#json_requestsToMe = simplejson.dumps(list(requestsToMe))
	#response
	#print json_requestsToMe
	return render_to_response('account/profile.html',{'user_profile':user_profile, 'searchForm':searchForm, 'liked':liked, 'n_likes':n_likes, 'isFriend':isFriend, 'existFriendRequest':existFriendRequest, 'requestsToMe':requestsToMe, 'json_requestsToMe': json_requestsToMe},context_instance=RequestContext(request))

@login_required(login_url='accounts/login')
def search(request):
	#para mostarar tambien el cuadro de busqueda en la pagina
	searchForm = SearchForm(request.POST)


	if request.method == 'POST':
		if searchForm.is_valid:
			texto_to_search = request.POST['searchText']

			#hacer busqueda si hay texto para buscar, mediante consulta a la base de datos y pasar el resultado
			if texto_to_search:
				words = texto_to_search.split()
				if len(words) == 1:
					resultSearch = User.objects.filter( Q(first_name__icontains = texto_to_search) | Q(last_name__icontains = texto_to_search) | Q(username__icontains = texto_to_search) )
				elif len(words) == 2:
					resultSearch = User.objects.filter( first_name__icontains = words[0], last_name__icontains = words[1] )
				else:
					resultSearch = User.objects.filter( first_name__icontains = words[0], last_name__icontains = words[1] + ' ' + words[2] )

				return render_to_response('account/search.html',{'showPerfilButtons':True,'searchForm':searchForm,'resultSearch':resultSearch}, context_instance=RequestContext(request))
	
	else:
		return render_to_response('account/search.html',{'showPerfilButtons':True,'searchForm':searchForm,'resultSearch':()}, context_instance=RequestContext(request))

@login_required(login_url='/')
def config_changepass(request):
	searchForm = SearchForm(request.POST)
	return render_to_response('account/cf-changepass.html', {'showPerfilButtons':True,'searchForm':searchForm}, context_instance=RequestContext(request))

@login_required(login_url='/')
def config_profile(request):
	searchForm = SearchForm(request.POST)

	if request.method == 'POST':
		# formulario enviado
		user_form = UserForm(request.POST, instance=request.user)
		perfil_form = PerfilForm(request.POST, instance=request.user.profile)

		if user_form.is_valid() and perfil_form.is_valid():
			# formulario validado correctamente
			user_form.save()
			perfil_form.save()
			return HttpResponseRedirect('/config/profile') #poner mas tarde, que muestre un mensaje de formulario aceptado

	else:
		# formulario inicial
		user_form = UserForm(instance=request.user)
		perfil_form = ProfileForm()



	return render_to_response('account/cf-profile.html', {'showPerfilButtons':True,'searchForm':searchForm, 'user_form':user_form, 'perfil_form':perfil_form}, context_instance=RequestContext(request))


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
            response="nolike"
        else:

            created = user.profile.add_like(UserProfile.objects.get(pk=slug))
            created.save()
            response="like"

    return HttpResponse(simplejson.dumps(response), mimetype='application/javascript')




def request_friend(request):
    print '>>>>>>> peticion amistad '
    response = "null"
    if request.method == 'POST':
        user = request.user
        slug = request.POST.get('slug', None)
        profileUserId = slug
        print str(profileUserId)
        try:
            print 'Paso 0'
            user_friend = user.profile.is_friend(profileUserId)
            print 'Paso 1'
        except ObjectDoesNotExist:
            user_friend = None

        
        if user_friend:
            response = "isfriend"
        else:
            response="inprogress"
            try:
                friend_request = user.profile.get_friend_request(UserProfile.objects.get(pk=slug))
            except ObjectDoesNotExist:
                friend_request = None

            if not friend_request:
               created = user.profile.add_friend_request(UserProfile.objects.get(pk=slug))
               created.save()

        print response               	

    return HttpResponse(simplejson.dumps(response), mimetype='application/javascript')



def add_friend(request):

    response = "null"
    if request.method == 'POST':
        user = request.user
        slug = request.POST.get('slug', None)
        profileUserId = slug
        try:
            user_friend = user.profile.is_friend(profileUserId)
        except ObjectDoesNotExist:
            user_friend = None

        if user_friend:
            user_friend.delete()
            response="nofriend"
        else:

            created = user.profile.add_friend(UserProfile.objects.get(pk=slug))
            created.save()
            response="friend"


    return HttpResponse(simplejson.dumps(response), mimetype='application/javascript')

@login_required(login_url='/')
def friends(request):

	try:
		#friends_4 = request.user.profile.get_friends_next4(1)
		friends = request.user.profile.get_friends()
	except ObjectDoesNotExist:
		friends = None

	friends_top4 = None
	if friends != None:
		if len(friends) > 4:
			#request.session['friends_list'] = simplejson.dumps(friends.values())
			#request.session['friends_list'] = list(friends)
			request.session['friends_list'] = serializers.serialize('json', friends)
			friends_top4 = friends[0:4]
		else:
			friends_top4 = friends

	
	return render_to_response('account/amigos.html', {'friends_top4':friends_top4}, context_instance=RequestContext(request))


def load_friends(request):


	friendslist = request.session.get('friends_list', None)
	b = request.session.get('friends_list', None)
	if friendslist == None:
		friends_4 = None
	else:
		friendslist = simplejson.loads(friendslist)
		print '>>>>>>> LISTA: '
		print (friendslist)
		if request.method == 'POST':
			slug = request.POST.get('slug', None)
			print '>>>>>>> LISTA: ' + slug
			n = int(slug) * 4
			#friends_4 = friendslist[n-4:n] # devolvera None si esta fuera de rango?
			friends_4 = friendslist


	return HttpResponse(simplejson.dumps(friends_4), mimetype='application/javascript')

