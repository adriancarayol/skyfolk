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

        form = PublicationForm(request.POST)
        userprofile = get_object_or_404(get_user_model(), pk=request.POST['userprofileid'])
        emitter = get_object_or_404(get_user_model(), pk=request.POST['emitterid'])
        response = False

        if form.is_valid():
            try:

                publication = form.save(commit=False)
                publication.writer = emitter.profile
                publication.profile = userprofile.profile
                publication.save()
                response = True

            except IntegrityError:
                pass


        return HttpResponse(simplejson.dumps(response), content_type='application/json')



