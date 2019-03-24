import json
import requests
from requests.exceptions import MissingSchema, RequestException
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework import status
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseForbidden
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from dash.models import DashboardEntry
from django.utils.decorators import method_decorator
from user_profile.models import Profile
from django.template.loader import render_to_string
from external_services.factory import ServiceFormFactory
from external_services.models import UserService
from loguru import logger


class LoadDynamicallyFormGivenService(APIView):
    renderer_classes = (TemplateHTMLRenderer, )

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        service_id = kwargs.pop('service_id')

        try:
            service = UserService.objects.get(user=request.user, id=service_id)
        except UserService.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        service_name = service.service.name.lower()
        template_name = "service/form_rendered.html"
        form = ServiceFormFactory.factory(service_name)()
        return Response({'form': form}, template_name=template_name)


class RetrieveInfoForServicePin(APIView):

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        pin_id = kwargs.pop('pin_id')
        page = request.GET.get('page', 1)
        
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

        service_info = json.loads(pin.plugin_data)

        if "service" not in service_info:
            return Response({'content': ''})

        try:
            user_service = UserService.objects.get(id=service_info["service"])
        except UserService.DoesNotExist:
            return Response({'content': ''})

        service_name = user_service.service.name.lower()
        template_name = 'service/{}/service_result.html'.format(service_name)

        try:
            response = requests.get('http://go_skyfolk:1800/service/{}/{}'.format(service_name, pin_id))
        except RequestException as e:
            logger.error(e)
            return Response({'content': ''})

        if response.status_code == 200:
            try:
                response_json = json.loads(response.json())

                if isinstance(response_json, dict):
                    response_json = [response_json]

                paginator = Paginator(response_json, 5)
                
                try:
                    results = paginator.page(page)
                except PageNotAnInteger:
                    results = paginator.page(1)
                except EmptyPage:
                    results = paginator.page(paginator.num_pages)

                rendered = render_to_string(template_name, {'results': results})
                return Response({'content': rendered})
            except Exception as e:
                print(e)

        return Response({'content': ''})
