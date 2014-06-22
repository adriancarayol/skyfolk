# from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django.utils import simplejson
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.models import User
from landing.models import Relationship, LikeProfile, UserProfile
from django.core.exceptions import ObjectDoesNotExist


def landing(request):
    return render_to_response(
        "account/base.html",
        RequestContext(request)
    )


def like_profile(request):

    response = "null"
    if request.method == 'POST':
        user = request.user
        slug = request.POST.get('slug', None)
        profileUserId = slug
        try:
            #user_liked = LikeProfile.objects.get(from_likeprofile=UserProfile.objects.get(user=user.id), to_likeprofile=UserProfile.objects.get(user=slug))
            user_liked = LikeProfile.objects.get(from_like=user.profile.id, to_like=profileUserId) #lo hace bien
        except ObjectDoesNotExist:
            user_liked = None

        if user_liked:
            user_liked.delete()
            response="nolike"
        else:
            created = LikeProfile.objects.create(from_like=UserProfile.objects.get(pk=user.profile.id), to_like=UserProfile.objects.get(pk=slug))
            created.save()
            response="like"


    return HttpResponse(simplejson.dumps(response), mimetype='application/javascript')