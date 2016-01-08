from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from user_profile import models
from user_profile.models import Relationship, LikeProfile, UserProfile


def news_and_updates(request):

    username = request.user.username

    user_profile = get_object_or_404(
            get_user_model(), username__iexact=username)

    print ('>>>>>>>>> NAME OF USER ' + user_profile.username)

    try:
        publications = user_profile.profile.get_myPublications()
    except ObjectDoesNotExist:
        publications = None

    return render_to_response('account/base_news.html', {'publications' : publications}, context_instance=RequestContext(request))

