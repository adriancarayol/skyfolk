from functools import wraps

from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import render, redirect
from django.urls import reverse

from user_groups.models import UserGroups, RequestGroup, LikeGroup


def user_can_view_group(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        groupname = kwargs.get('groupname', None)
        user = request.user

        try:
            group_profile = UserGroups.objects.select_related('owner').get(slug=groupname)
        except UserGroups.DoesNotExist:
            raise Http404

        is_member = True
        if not group_profile.is_public and group_profile.owner_id != user.id:
            if not group_profile.users.filter(id=user.id).exists():
                is_member = False

        if not is_member:
            try:
                friend_request = RequestGroup.objects.get_follow_request(
                    from_profile=user.id, to_group=group_profile)
            except ObjectDoesNotExist:
                friend_request = None

            context = {
                'group_profile': group_profile,
                'interests': group_profile.tags.all(),
                'friend_request': friend_request,
                'likes': LikeGroup.objects.filter(to_like=group_profile).count(),
                'user_like_group': LikeGroup.objects.has_like(group_id=group_profile, user_id=user),
                'users_in_group': group_profile.users.count()
            }

            return render(request, 'groups/group_profile_no_member.html', context)

        return function(request, *args, **kwargs)

    return wrap


def user_can_view_group_info(function):
    """
    Executes a HTTP 302 redirect after the view finishes processing. If a value is
    returned, it is ignored. Allows for the view url to be callable so the
    reverse() lookup can be used.

    @redirect('http://www.google.com/')
    def goto_google(request):
        pass

    @redirect(lambda: reverse('some_viewname'))
    def do_redirect(request):
        ...

    """

    @wraps(function)
    def inner(request, *args, **kwargs):
        groupname = kwargs.get('groupname', None)

        if not groupname:
            groupname = kwargs.get('slug', None)

        user = request.user

        try:
            group_profile = UserGroups.objects.select_related('owner').get(slug=groupname)
        except UserGroups.DoesNotExist:
            raise Http404

        if not group_profile.is_public and group_profile.owner_id != user.id:
            is_member = user.user_groups.filter(id=group_profile.id).exists()
            if not is_member:
                return redirect(reverse('user_groups:group-profile', kwargs={'groupname': groupname}))

        return function(request, *args, **kwargs)

    return inner
