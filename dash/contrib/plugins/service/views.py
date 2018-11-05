import json
import requests
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseForbidden
from dash.models import DashboardEntry
from django.utils.decorators import method_decorator
from user_profile.models import Profile
from django.template.loader import render_to_string


class RetrieveInfoForServicePin(APIView):

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        pin_id = kwargs.pop('pin_id')

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

        if privacity and privacity != 'all':
            return HttpResponseForbidden()

        # response = requests.get('http://outside:1800/service/{}/'.format(pin_id))

        # if response.status_code != 200:
        try:
            response_json = [
                {
                'text': 'FOO',
                'account': 'Adrian',
                'link': 'YEE'
                },
                {
                'text': 'FOO2',
                'account': 'Adrian',
                'link': 'YEE'
                }
            ]
            rendered = render_to_string('service/service_result.html', {'results': response_json})
            return Response({'content': rendered})
        except Exception:
            pass

        return Response({'content': ''})