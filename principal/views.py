#from django.shortcuts import render
#from principal.models import Receta , Comentario
#from principal.forms import RecetaForm, ComentarioForm, ContactoForm
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response , get_object_or_404, render
from django.template import RequestContext
from principal.forms import UserCreateForm, AuthForm
#from principal.forms import UserCreationForm
from django.core.mail import EmailMessage
#para la gestion de usuarios y autentificacion
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from principal.forms import SearchForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import hashlib

# Create your views here.
"""
def inicio(request):
	return render_to_response('inicio.html',context_instance=RequestContext(request))
"""
def new_user(request):
	if request.method=='POST':
		form = UserCreateForm(request.POST)
		if form.is_valid:
			form.save()
			return HttpResponseRedirect('/')
	else:
		form = UserCreateForm()
	return render_to_response('newuser.html', {'form':form}, context_instance=RequestContext(request))

def inicio(request):
	if not request.user.is_anonymous():
		return HttpResponseRedirect('/profile/' + str(request.user.username))
	if request.method == 'POST':
		form = AuthForm(request.POST)
		if form.is_valid:
			usuario = request.POST['username']
			clave = request.POST['password']
			acceso = authenticate(username=usuario,password=clave)
			if acceso is not None:
				if acceso.is_active:
					login(request, acceso)
					return HttpResponseRedirect('/profile/' + str(request.user.username))
				else:
					return render_to_response('inactive.html', context_instance=RequestContext(request))
			else:
				return render_to_response('nologin.html', context_instance=RequestContext(request))
	else:
		form = AuthForm()
		#messages.info(request, 'Three credits remain in your account.')
	return render_to_response('inicio.html', {'form':form}, context_instance=RequestContext(request))

@login_required(login_url='/')
def profile_view(request, username):
	userProfile = User.objects.get(username__iexact = username)
	isProfileUser = False
	requestUsername = request.user.username #esto es para que una vez cargada la pagina de perfil, al pulsar buscar hace falta poner el nombre del usuario que visita la pagina

	if not request.user.is_anonymous():
		if request.user.username == userProfile.username:
			#el que ve el perfil es el usuario del perfil
			isProfileUser = True

	if request.method == 'POST':
		searchForm = SearchForm(request.POST)
		if searchForm.is_valid:
			searchText = request.POST['searchText']
			#hacer busqueda mediante consulta a la base de datos y redireccionar a search.html con los datos

	else:
		searchForm = SearchForm(request.POST)

	return render_to_response('profile.html',{'userProfile':userProfile,'isProfileUser':isProfileUser,'searchForm':searchForm,'requestUsername':requestUsername},context_instance=RequestContext(request))


@login_required(login_url='/')
def search(request, username):

	#return render_to_response('profile.html',{'userProfile':userProfile,'isProfileUser':isProfileUser},context_instance=RequestContext(request))
	return render_to_response('search.html', context_instance=RequestContext(request))

@login_required(login_url='/')
def out_session(request):
	logout(request)
	return HttpResponseRedirect('/')

