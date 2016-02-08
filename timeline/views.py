import json

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from publications.models import Publication
from timeline.models import Timeline


def addToTimeline(request):
    print('>>>>>>>>>>>>> PETITION AJAX ADD TO TIMELINE')
    if request.POST:
        obj_userprofile = get_object_or_404(
            get_user_model(), pk=request.POST['userprofile_id']
        )
        print(obj_userprofile)
        # Obtener perfil al que añadir comentario al timeline
        obj_profile = get_object_or_404(
            get_user_model(), pk=request.user.id
        )

        obj_pub = request.POST['publication_id']
        #print(obj_pub)
        try:
            pubToAdd = Publication.objects.get(pk=obj_pub)
            # print(pubToAdd.content)
            t = Timeline(content=pubToAdd.content, author=obj_userprofile.profile,
            profile=obj_profile.profile)
            t.save()
            # print(t.content)
            response = True
        except ObjectDoesNotExist:
            response = False

        return HttpResponse(json.dumps(response), content_type='application/json')
