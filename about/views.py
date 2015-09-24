from django.shortcuts import render_to_response, get_object_or_404, render
from django.template import RequestContext, loader

def about(request,view):
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
