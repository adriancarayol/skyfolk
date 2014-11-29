from django.shortcuts import render, render_to_response , get_object_or_404
from publications.forms import PublicationForm
from django.http import HttpResponse
from django.db import IntegrityError
from django.utils import simplejson
from django.contrib.auth import get_user_model

# Create your views here.
def publication_form(request):
    print '>>>>>>>> PETICION AJAX PUBLICACION'
    if request.POST:
        print '>>> paso 0'
        form = PublicationForm(request.POST)
        userprofile = get_object_or_404(get_user_model(), pk=request.POST['userprofileid'])
        emitter = get_object_or_404(get_user_model(), pk=request.POST['emitterid'])
        response = False
        print '>>> paso 1'
        if form.is_valid():
            try:
                print '>>> paso 1'
                publication = form.save(commit=False)
                publication.writer = emitter.profile
                publication.profile = userprofile.profile
                publication.save()
                response = True
                print '>>> paso 2'
            except IntegrityError:
                form._errors["content"] = "content field error"
                form._errors["writer"] = "writer field error"
                form._errors["profile"] = "profile field error"


        return HttpResponse(simplejson.dumps(response), content_type='application/json')



