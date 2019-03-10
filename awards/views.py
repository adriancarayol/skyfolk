from django.db.models import Sum
from badgify.models import Award, Badge
from awards.models import UserRank
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404
from django.http import HttpResponseForbidden
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from user_profile.models import Profile


class UserAwards(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "awards/my-awards.html"

    @staticmethod
    def get_points_and_last_rank(profile):
        user_id = profile.user_id
        points = Badge.objects.filter(users__id=user_id).aggregate(total_points=Sum('points'))['total_points'] or 0
        last_rank = UserRank.objects.filter(users__id=user_id).order_by('-reached_with').first()
        return points, last_rank

    def get(self, request, *args, **kwargs):
        user_id = kwargs.pop('user_id', None)

        if not user_id:
            raise Http404

        try:
            profile = Profile.objects.get(user_id=user_id)
            request_user = Profile.objects.get(user_id=request.user.id)
        except Profile.DoesNotExist:
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

        points, last_rank = self.get_points_and_last_rank(profile)

        return Response({'awards': awards, 'user_id': user_id, 'total_points': points, 'last_rank': last_rank})
