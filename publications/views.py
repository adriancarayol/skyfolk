from django.shortcuts import render, render_to_response , get_object_or_404
from publications.forms import PublicationForm
from django.http import HttpResponse
from django.db import IntegrityError
import json
from django.contrib.auth import get_user_model
from emoji import *
from django.utils.safestring import mark_safe

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
                publication.content = Emoji.replace(mark_safe(publication.content))
                print(str(userprofile.profile))
                print(str(emitter.profile))
                publication.save()
                response = True
            except IntegrityError:
                pass

        return HttpResponse(json.dumps(response), content_type='application/json')


def delete_publication(request):
    print ('>>>>>>>> PETICION AJAX BORRAR PUBLICACION')
    if request.POST:
        # print request.POST['userprofile_id']
        # print request.POST['publication_id']
        obj_userprofile = get_object_or_404(
                                            get_user_model(),
                                            pk=request.POST['userprofile_id']
                                            )
        print (obj_userprofile)
        try:
            obj_userprofile.profile.remove_publication(
                                publicationid=request.POST['publication_id']
                                )

            response = True
        except:
            response = False

        return HttpResponse(json.dumps(response),
                                content_type='application/json'
                               )


def load_publications(request):

    print('>>>>>> PETICION AJAX, CARGAR MAS PUBLICACIONES')
    publicationslist = request.session.get('publications_list', None)
    if publicationslist == None:
        publications_next = None
    else:
        publicationslist = json.loads(publicationslist)
        if request.method == 'POST':
            slug = request.POST.get('slug', None)
            print('>>>>>>> SLUG: ' + slug)
            n = int(slug) * 15
            publications_next = publicationslist[n-15:n]
            print('>>>>>>> LISTA: ')
            print(publications_next)

    return HttpResponse(json.dumps(list(publications_next)), content_type='application/json')

def addLike(request):
    if request.POST:
        obj_userprofile = get_object_or_404(
            get_user_model(),
            pk=request.POST['userprofile_id']
        )
        try:
            obj_userprofile.profile.add_like(
                    publicationid=request.POST['publication_id']
            )
            response = True
        except:
            response = False
    return HttpResponse(json.dump(response), content_type='application/json')
