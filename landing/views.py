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
            user_liked = user.profile.has_like(profileUserId)
        except ObjectDoesNotExist:
            user_liked = None

        if user_liked:
            user_liked.delete()
            response="nolike"
        else:

            created = user.profile.add_like(UserProfile.objects.get(pk=slug))
            created.save()
            response="like"


    return HttpResponse(simplejson.dumps(response), mimetype='application/javascript')