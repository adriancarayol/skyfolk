import json

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from publications.models import Publication

def add_to_timeline(request):
    response = False
    print('>>>>>>>>>>>>> PETITION AJAX ADD TO TIMELINE')
    if request.POST:
        obj_userprofile = get_object_or_404(
            get_user_model(), pk=request.POST['userprofile_id']
        )

        obj_pub = request.POST['publication_id']

        try:
            pub_to_add = Publication.objects.get(pk=obj_pub)
            t, created = Timeline.objects.get_or_create(publication=pub_to_add, author=pub_to_add.author.profile,
                                                        profile=obj_userprofile.profile)

            if created:
                print('Añadir nuevo timelime al perfil del usuario')
                pub_to_add.user_share_me.add(request.user)
                pub_to_add.save()
                response = True
            elif not created:
                print('Ya existe en el timeline del usuario')
                response = True
            print('Compartido el comentario %d -> %d veces' % (pub_to_add.id, pub_to_add.user_share_me.count()))
        except ObjectDoesNotExist:
            response = False

        return HttpResponse(json.dumps(response), content_type='application/json')


def remove_timeline(request):
    print('>>>>>>>> PETICION AJAX BORRAR TIMELINE')
    if request.POST:
        profile_id = request.POST['userprofile_id']
        obj_userprofile = get_object_or_404(
            get_user_model(),
            pk=profile_id
        )
        try:
            timeline = request.POST['timeline_id']
            Timeline.objects.remove_timeline(timeline, obj_userprofile)
            response = True
        except ObjectDoesNotExist:
            response = False

        return HttpResponse(json.dumps(response),
                            content_type='application/json'
                            )
