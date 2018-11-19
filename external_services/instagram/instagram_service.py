import requests
import json
from external_services.models import Services, UserService
from django.urls import reverse
from django.db import IntegrityError


class InstagramService(object):
    client_id = 'dec537046acd40ea8c5365d36a8ee7a3'
    client_secret = 'ab13542b945e44828c597a1ef42ccf39'

    def __init__(self, **kwargs):
        self.callback = 'http://0.0.0.0:8000/external/services/instagram/callback/'
        self.auth_url = 'https://api.instagram.com/oauth/authorize/?client_id={client_id}' \
                        '&redirect_uri={redirect_url}&response_type=code'.format(
                         client_id='dec537046acd40ea8c5365d36a8ee7a3', redirect_url=self.callback)

    @classmethod
    def exchange_code_for_access_token(cls, code, redirect_uri, **kwargs):
        url = u'https://api.instagram.com/oauth/access_token'
        data = {
            u'client_id': cls.client_id,
            u'client_secret': cls.client_secret,
            u'code': code,
            u'grant_type': u'authorization_code',
            u'redirect_uri': redirect_uri
        }

        response = requests.post(url, data=data)

        account_data = json.loads(response.content)

        return account_data

    @staticmethod
    def get_auth_url():
        return reverse('external_services:instagram-service:connect-instagram-service')

    def auth(self, request):
        return self.get_request_token(request)

    def get_request_token(self, request):
        return self.auth_url

    def callback_oauth1(self, request):
        code = request.GET.get('code')
        data = self.exchange_code_for_access_token(code, self.callback)

        try:
            service = Services.objects.get(name="Instagram", status=True)
        except Services.DoesNotExist:
            return '/'

        try:
            user_service = UserService.objects.get(user=request.user, service=service)
            user_service.auth_token = data.get('access_token')
            user_service.save()
        except UserService.DoesNotExist as e:
            try:
                UserService.objects.create(user=request.user, service=service,
                                           auth_token=data.get('access_token'),
                                           auth_token_secret='')
            except IntegrityError as e:
                pass

        return '/'
