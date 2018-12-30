import requests
import json
from external_services.models import Services, UserService
from django.urls import reverse
from django.db import IntegrityError


class InstagramService(object):
    client_id = '8d08509d6ba6416d8420e2de472e5f51'
    client_secret = '4826451fd2294d8e902e583fbc90f95a'

    def __init__(self, **kwargs):
        self.callback = reverse('external_services:instagram-service:callback-instagram-service')

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
        callback = request.build_absolute_uri(self.callback)
        auth_url = 'https://api.instagram.com/oauth/authorize/?client_id={client_id}' \
                   '&redirect_uri={redirect_url}&response_type=code'.format(
                    client_id='dec537046acd40ea8c5365d36a8ee7a3', redirect_url=callback)
        return auth_url

    def callback_oauth1(self, request):
        code = request.GET.get('code')
        callback = request.build_absolute_uri(self.callback)

        data = self.exchange_code_for_access_token(code, callback)

        try:
            service = Services.objects.get(name="Instagram", status=True)
        except Services.DoesNotExist:
            return reverse('external_services:all-external-services')

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

        return reverse('external_services:all-external-services')
