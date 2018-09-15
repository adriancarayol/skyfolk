from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from neomodel import db
from user_profile.models import Profile
from django.http import Http404, HttpResponseForbidden


class ProfileInterests(APIView):
    """
    List interests of user profile
    """
    authentication_classes = (authentication.SessionAuthentication,
                              authentication.BasicAuthentication)

    def get(self, request, username):
        try:
            profile = Profile.objects.get(user__username=username)
            request_user = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            raise Http404()

        privacity = profile.is_visible(request_user)

        if privacity and privacity != 'all':
            return HttpResponseForbidden()

        interests = profile.tags.names()[10:]
        return Response(interests)
