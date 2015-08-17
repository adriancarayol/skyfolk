from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404, render
from django.template import RequestContext, loader
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db.models import Q
from user_profile.models import Relationship, LikeProfile, UserProfile
from publications.models import Publication
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import simplejson
#from django.utils import simplejson as json
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.safestring import mark_safe
#allauth
from allauth.account.views import PasswordChangeView

@login_required(login_url='accounts/login')
def relaciones_user(request,username):
	user = request.user
	user_profile = get_object_or_404(get_user_model(), username__iexact=username)

	try:
		friends = user_profile.profile.get_friends()
	except ObjectDoesNotExist:
		friends = None

	bestFriendsOrBestFamily = None

	if friends != None:
		if len(friends) >= 1:
			request.session['friends_list'] = simplejson.dumps(list(friends))
			bestFriendsOrBestFamily = friends[0:9]
		else:
			bestFriendsOrBestFamily = friends



	return render_to_response('account/afinidad.html', {'user_profile': user_profile,'bestFriendsOrBestFamily':bestFriendsOrBestFamily}, context_instance=RequestContext(request))
