#from django.shortcuts import render
#from index.models import Receta , Comentario
#from index.forms import RecetaForm, ComentarioForm, ContactoForm
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response , get_object_or_404, render
from django.template import RequestContext
from index.forms import UserCreateForm, AuthForm
#from index.forms import UserCreationForm
from django.core.mail import EmailMessage
#para la gestion de usuarios y autentificacion
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from index.forms import SearchForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import hashlib
from django.db.models import Q
from django.core.urlresolvers import reverse
from userena import views as userena_views
from userena.utils import get_user_model

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


	#requestUsername = request.user.username #esto es para que una vez cargada la pagina de perfil, al pulsar buscar hace falta poner el nombre del usuario que visita la pagina
	#para mostarar el cuadro de busqueda en la pagina:
	searchForm = SearchForm(request.POST)

	user = get_object_or_404(get_user_model(), username__iexact=username)
	profile = user.get_profile()
	return render_to_response('profile.html',{'profile':profile,'searchForm':searchForm},context_instance=RequestContext(request))


@login_required(login_url='/')
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

				return render_to_response('search.html',{'showPerfilButtons':True,'searchForm':searchForm,'resultSearch':resultSearch}, context_instance=RequestContext(request))
	
	else:
		return render_to_response('search.html',{'showPerfilButtons':True,'searchForm':searchForm,'resultSearch':()}, context_instance=RequestContext(request))


@login_required(login_url='/')
def news_event(request):
	return render_to_response('columnas.html', context_instance=RequestContext(request))
		
@login_required(login_url='/')
def config_profile(request):
	searchForm = SearchForm(request.POST)
	return render_to_response('cf.html', {'showPerfilButtons':True,'searchForm':searchForm}, context_instance=RequestContext(request))

@login_required(login_url='/')
def config_profile2(request):
	searchForm = SearchForm(request.POST)
	return render_to_response('cf2.html', {'showPerfilButtons':True,'searchForm':searchForm}, context_instance=RequestContext(request))
	
@login_required(login_url='/')
def friends(request):
	return render_to_response('amigos.html', context_instance=RequestContext(request))
	
@login_required(login_url='/')
def out_session(request):
	logout(request)
	return HttpResponseRedirect('/')

#..........................
#	usernea views
#.........................

#.........................
# Vista de perfil que sobreescribe al de userena
# Carlos Canicio Almendros
#..........................
def myprofile_detail(request,username):
    # do stuff before userena signup view is called

    searchForm = SearchForm(request.POST)

    # call the original view
    response = userena_views.profile_detail(request,username,extra_context={'searchForm':searchForm})

    # do stuff after userena signup view is done
    #response.extra_context['searchForm'] = searchForm

    # return the response
    return response