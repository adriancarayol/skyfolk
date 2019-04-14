import json
import requests
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseForbidden
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from dash.models import DashboardEntry
from django.utils.decorators import method_decorator
from user_profile.models import Profile, RelationShipProfile
from user_profile.constants import FOLLOWING
from django.template.loader import render_to_string


class RetrieveInfoForFollowsPin(APIView):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        pin_id = kwargs.pop("pin_id")
        page = request.GET.get("page", 25)

        try:
            pin = DashboardEntry._default_manager.get(id=pin_id)
        except DashboardEntry.DoesNotExist:
            raise Http404

        try:
            profile = Profile.objects.get(user_id=pin.user.id)
            request_user = Profile.objects.get(user_id=request.user.id)
        except Profile.DoesNotExist:
            raise Http404

        privacity = profile.is_visible(request_user)

        if privacity and privacity != "all":
            return HttpResponseForbidden()

        follows = (
            RelationShipProfile.objects.filter(
                from_profile__user=pin.user, type=FOLLOWING
            )
            .select_related("to_profile", "to_profile__user")
            .prefetch_related("to_profile__tags")
        )

        paginator = Paginator(follows, 1)

        try:
            following = paginator.page(page)
        except PageNotAnInteger:
            following = paginator.page(1)
        except EmptyPage:
            following = paginator.page(paginator.num_pages)

        rendered = render_to_string(
            "follows/follows_page.html", {"friends_top12": following}
        )
        return Response({"content": rendered})
