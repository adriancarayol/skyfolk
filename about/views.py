from django.shortcuts import render_to_response, get_object_or_404, render
from django.template import RequestContext, loader

def about(request,view):
    if view == 'home':
        plantilla = 'aboutskyfolk/aboutSkyfolk.html'
    elif view == 'us':
        plantilla = 'aboutskyfolk/aboutUs.html'
    elif view == 'project':
        plantilla = 'aboutskyfolk/project.html'
    elif view == 'team':
        plantilla = 'aboutskyfolk/team.html'
    elif view == "special":
        plantilla = 'aboutskyfolk/special.html'

    return render(request,plantilla)
