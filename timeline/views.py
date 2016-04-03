import json

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from publications.models import Publication
from timeline.models import Timeline

# TODO
def addToTimeline(request):
    response = False
    print('>>>>>>>>>>>>> PETITION AJAX ADD TO TIMELINE')
    if request.POST:
        obj_userprofile = get_object_or_404(
            get_user_model(), pk=request.POST['userprofile_id']
        )

        obj_pub = request.POST['publication_id']

        try:
            pub_to_add = Publication.objects.get(pk=obj_pub)
            t, created = Timeline.objects.get_or_create(publication=pub_to_add, author=pub_to_add.author,
                                                        profile=obj_userprofile.profile,
                                                        content=pub_to_add.content)
            print(t.users_add_me.all())
            if created:
                print('Añadir nuevo timelime')
                t.users_add_me.add(request.user)
                t.save()
                response = True
            elif not created:
                print('Eliminar timeline')
                t.users_add_me.remove(request.user)
                t.save()
                response = True
        except ObjectDoesNotExist:
            response = False

        return HttpResponse(json.dumps(response), content_type='application/json')

def removeTimeline(request):
    print('>>>>>>>> PETICION AJAX BORRAR TIMELINE')
    if request.POST:
        # print request.POST['userprofile_id']
        # print request.POST['publication_id']
        obj_userprofile = get_object_or_404(
            get_user_model(),
            pk=request.POST['userprofile_id']
        )
        print(obj_userprofile.pk)
        print(request.user.pk)
        try:
            obj_userprofile.profile.remove_timeline(
                timeline_id=request.POST['timeline_id']
            )
            response = True

        except ObjectDoesNotExist:
            response = False

        return HttpResponse(json.dumps(response),
                    content_type='application/json'
                )
