from django.shortcuts import render, render_to_response , get_object_or_404
from publications.forms import PublicationForm
from django.http import HttpResponse
from django.db import IntegrityError
import json
from django.contrib.auth import get_user_model


# Create your views here.
def publication_form(request):
    print('>>>>>>>> PETICION AJAX PUBLICACION')
    if request.POST:

        form = PublicationForm(request.POST)
        userprofile = get_object_or_404(get_user_model(), pk=request.POST['userprofileid'])
        emitter = get_object_or_404(get_user_model(), pk=request.POST['emitterid'])
        response = False

        if form.is_valid():
            try:
                publication = form.save(commit=False)
                publication.writer = emitter.profile
                publication.profile = userprofile.profile
                print(str(userprofile.profile))
                print(str(emitter.profile))
                publication.save()
                response = True
            except IntegrityError:
                pass

        return HttpResponse(json.dumps(response), content_type='application/json')
    
def load_publications(request):

    print('>>>>>> PETICION AJAX, CARGAR MAS PUBLICACIONES')
    publicationslist = request.session.get('publications_list', None)
    if publicationslist == None:
        publications_next = None
    else:
        publicationslist = simplejson.loads(publicationslist)
        if request.method == 'POST':
            slug = request.POST.get('slug', None)
            print('>>>>>>> SLUG: ' + slug)
            n = int(slug) * 15
            publications_next = publicationslist[n-15:n]
            print('>>>>>>> LISTA: ')
            print(publications_next)

    return HttpResponse(json.dumps(list(publications_next)), content_type='application/json')



