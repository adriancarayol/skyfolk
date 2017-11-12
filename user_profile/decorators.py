from functools import wraps

from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse

from user_profile.models import Profile
from user_profile.node_models import NodeProfile


def user_can_view_profile_info(function):
    @wraps(function)
    def inner(request, *args, **kwargs):
        username = kwargs.get('username', None)
        user = request.user

        try:
            n = Profile.objects.get(user_id=user.id)
            m = Profile.objects.get(user__username=username)
        except Profile.DoesNotExist:
            raise Http404

        privacity = m.is_visible(n)

        if privacity and privacity != 'all':
            return redirect(reverse('user_profile:profile', kwargs={'username': username}))
        return function(request, *args, **kwargs)

    return inner
