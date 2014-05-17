from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response , get_object_or_404, render
from django.template import RequestContext
from user_profile.forms import SearchForm
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db.models import Q

# Create your views here.
@login_required(login_url='accounts/login')
def profile_view(request, username):


	#requestUsername = request.user.username #esto es para que una vez cargada la pagina de perfil, al pulsar buscar hace falta poner el nombre del usuario que visita la pagina
	#para mostarar el cuadro de busqueda en la pagina:
	searchForm = SearchForm(request.POST)

	userProfile = get_object_or_404(get_user_model(), username__iexact=username)
	#profile = user.get_profile()
	#return render_to_response('profile.html',{'profile':profile,'searchForm':searchForm},context_instance=RequestContext(request))
	return render_to_response('account/profile.html',{'userProfile':userProfile, 'searchForm':searchForm},context_instance=RequestContext(request))


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
def config(request, type_form):
	searchForm = SearchForm(request.POST)

	if type_form == 'cf-changepass':
		return render_to_response('account/cf-changepass.html', {'showPerfilButtons':True,'searchForm':searchForm}, context_instance=RequestContext(request))
	elif type_form == 'cf-profile':
		return render_to_response('account/cf-profile.html', {'showPerfilButtons':True,'searchForm':searchForm}, context_instance=RequestContext(request))
