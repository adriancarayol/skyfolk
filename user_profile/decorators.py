from functools import wraps

from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse

from user_profile.models import NodeProfile


def user_can_view_profile_info(function):
    @wraps(function)
    def inner(request, *args, **kwargs):
        username = kwargs.get('username', None)
        user = request.user

        try:
            n = NodeProfile.nodes.get(user_id=user.id)
            m = NodeProfile.nodes.get(title=username)
        except NodeProfile.DoesNotExist:
            raise Http404

        privacity = m.is_visible(n)

        if privacity and privacity != 'all':
            return redirect(reverse('user_profile:profile', kwargs={'username': username}))
        return function(request, *args, **kwargs)

    return inner
