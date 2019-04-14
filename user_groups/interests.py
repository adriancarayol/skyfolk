from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.http import Http404
from user_groups.models import UserGroups
from django.http import HttpResponseForbidden


class GroupInterests(APIView):
    """
    List interests of user profile
    """

    authentication_classes = (
        authentication.SessionAuthentication,
        authentication.BasicAuthentication,
    )

    def get(self, request, group_slug):
        try:
            user_group = UserGroups.objects.get(slug=group_slug)

            if (
                not user_group.is_public
                and not user_group.users.filter(id=request.user.id).exists()
            ):
                return HttpResponseForbidden()

            interests = user_group.tags.names()[10:]
            return Response(interests)
        except UserGroups.DoesNotExist:
            raise Http404("El grupo {} no existe".format(group_slug))
