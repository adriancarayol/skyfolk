# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.files import File
from .forms import EmailForm

def home(request):
    # Si obtenemos la informacion correcta...
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            emails = form.cleaned_data['email']
                 # Si estamos trabajando en local ->
            #with open('landing/mailcore/emails.txt', 'a+') as f:
            with open('/var/www/skyfolk/run/app/emails.txt', 'a+') as f:
                myEmails = File(f)
                myEmails.write('{}\n'.format(emails))
                myEmails.close()

            # print("emails -> {}".format(emails))
            return HttpResponseRedirect('/confirmation/')
    else:
        form = EmailForm()
    return render(request, "index.html", {'form': form})

def confirmation(request):
    return render(request,"confirmation.html",{})

def team(request):
    return render(request, "team.html", {})
