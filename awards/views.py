from badgify.models import Award
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404
from django.http import HttpResponseForbidden
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from user_profile.node_models import NodeProfile


class UserAwards(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "awards/my-awards.html"

    def get(self, request, *args, **kwargs):
        user_id = kwargs.pop('user_id', None)

        if not user_id:
            raise Http404

        try:
            profile = NodeProfile.nodes.get(user_id=user_id)
            request_user = NodeProfile.nodes.get(user_id=request.user.id)
        except User.DoesNotExist:
            raise Http404

        privacity = profile.is_visible(request_user)
        if privacity and privacity != 'all':
            return HttpResponseForbidden()

        queryset = Award.objects.filter(user_id=profile.user_id)
        paginator = Paginator(queryset, 12)

        page = request.GET.get('page', 1)

        try:
            awards = paginator.page(page)
        except PageNotAnInteger:
            awards = paginator.page(1)
        except EmptyPage:
            awards = paginator.page(paginator.num_pages)

        return Response({'awards': awards, 'user_id': user_id})
