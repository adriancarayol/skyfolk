from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response , get_object_or_404, render
from django.template import RequestContext

# Create your views here.
@login_required(login_url='accounts/login')
def profile_view(request, username):


	#requestUsername = request.user.username #esto es para que una vez cargada la pagina de perfil, al pulsar buscar hace falta poner el nombre del usuario que visita la pagina
	#para mostarar el cuadro de busqueda en la pagina:
	#searchForm = SearchForm(request.POST)

	#user = get_object_or_404(get_user_model(), username__iexact=username)
	#profile = user.get_profile()
	#return render_to_response('profile.html',{'profile':profile,'searchForm':searchForm},context_instance=RequestContext(request))
	return render_to_response('account/profile.html',context_instance=RequestContext(request))