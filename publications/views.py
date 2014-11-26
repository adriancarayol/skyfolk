from django.shortcuts import render
from publications.forms import PublicationForm
from django.http import HttpResponse
from django.db import IntegrityError
from django.utils import simplejson

# Create your views here.
def publication_form(request):
    if request.POST:
        response = False
        form = PublicationForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                response = True
            except IntegrityError:
                form._errors["content"] = "content field error"
                form._errors["writer"] = "writer field error"
                form._errors["profile"] = "profile field error"


        return HttpResponse(simplejson.dumps(response), content_type='application/json')



