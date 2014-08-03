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

# Create your views here.
@login_required(login_url='accounts/login')
def profile_view(request, username):


	#para mostarar el cuadro de busqueda en la pagina:
	searchForm = SearchForm(request.POST)

	user_profile = get_object_or_404(get_user_model(), username__iexact=username)

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

	#response
	return render_to_response('account/profile.html',{'user_profile':user_profile, 'searchForm':searchForm, 'liked':liked, 'n_likes':n_likes, 'isFriend':isFriend},context_instance=RequestContext(request))

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
	if friends != None and len(friends) > 4:
		request.session['friends_list'] = list(friends)
		friends_top4 = friends[0:4]
		print friends_top4

	
	return render_to_response('account/amigos.html', {'friends_top4':friends_top4}, context_instance=RequestContext(request))


def load_friends(request):


	friendslist = request.session.get('friends_list', None)
	if friendslist == None:
		friends_4 = None
	else:

		if request.method == 'POST':
			slug = request.POST.get('slug', None)
			n = int(slug) * 4
			friends_4 = request.session['friends_list'][n-4:n] # devolvera None si esta fuera de rango?


	return HttpResponse(simplejson.dumps(friends_4), mimetype='application/javascript')

