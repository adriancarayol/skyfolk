from django.shortcuts import render
from django.views.generic import TemplateView


def about(request, view):
    plantilla = None
    if view == 'home':
        plantilla = 'about/aboutSkyfolk.html'
    elif view == 'us':
        plantilla = 'about/aboutUs.html'
    elif view == 'project':
        plantilla = 'about/project.html'
    elif view == 'team':
        plantilla = 'about/team.html'
    elif view == "special":
        plantilla = 'about/special.html'

    return render(request,plantilla)
