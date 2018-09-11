from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.http import Http404
from user_groups.models import UserGroups


class GroupInterests(APIView):
    """
    List interests of user profile
    """
    authentication_classes = (authentication.SessionAuthentication, 
        authentication.BasicAuthentication)
    permission_classes = (permissions.IsAdminUser,)

    def get(self, request, group_slug):
        try:
            user_group = UserGroups.objects.get(slug=group_slug)
            interests = user_group.tags.all().values_list('name')[10:],
            return Response(interests)  
        except UserGroups.DoesNotExist:
            raise Http404('El grupo {} no existe'.format(group_slug))

        return Response([])

        