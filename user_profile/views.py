from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response , get_object_or_404, render
from django.template import RequestContext, loader
from user_profile.forms import SearchForm
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db.models import Q
from forms import ProfileForm, UserForm
from landing.models import UserProfile

# Create your views here.
@login_required(login_url='accounts/login')
def profile_view(request, username):


	#requestUsername = request.user.username #esto es para que una vez cargada la pagina de perfil, al pulsar buscar hace falta poner el nombre del usuario que visita la pagina
	#para mostarar el cuadro de busqueda en la pagina:
	searchForm = SearchForm(request.POST)

	user_profile = get_object_or_404(get_user_model(), username__iexact=username)
	#profile = user.get_profile()
	#return render_to_response('profile.html',{'profile':profile,'searchForm':searchForm},context_instance=RequestContext(request))
	return render_to_response('account/profile.html',{'user_profile':user_profile, 'searchForm':searchForm},context_instance=RequestContext(request))


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
