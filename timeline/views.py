from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from publications.models import Publication
from timeline.models import Timeline
import json

def addToTimeline(request):
    print('>>>>>>>>>>>>> PETITION AJAX ADD TO TIMELINE')
    if request.POST:
        obj_userprofile = get_object_or_404(
            get_user_model(), pk=request.POST['userprofile_id']
        )
        print(obj_userprofile)
        obj_pub = request.POST['publication_id']
        print(obj_pub)
        try:
            content = Publication.objects.get(pk=obj_pub)
            print(content.content)
            response = True
        except:
            response = False

        return HttpResponse(json.dumps(response), content_type='application/json')