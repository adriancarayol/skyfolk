import numpy as np
import math
from badgify.models import Award, Badge
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

    def percentage(self, part, total):
        return math.trunc((part * 100.0) / total)

    def calculate_exp(self, profile):
        badges = Badge.objects.filter(users=profile.user).values('points', 'category')
        all_badges = Badge.objects.all().values('points', 'category')
        points = np.sum([x['points'] for x in badges])
        exp = {}
        total_exp = {}

        for badge in all_badges:
            if badge['category'] in total_exp:
                total_exp[badge['category']] += badge['points']
            else:
                total_exp[badge['category']] = badge['points']

        for badge in badges:
            if badge['category'] in exp:
                exp[badge['category']] += badge['points']
            else:
                exp[badge['category']] = badge['points']

        percentages = {}

        for key, value in exp.items():
            percentages[key] = self.percentage(value, total_exp[key])

        return percentages, points

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

        percentages, points = self.calculate_exp(profile)

        return Response({'awards': awards, 'user_id': user_id, 'total_points': points, 'type_of_user': percentages})
