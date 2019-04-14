import os
import requests
import json
from external_services.models import Services, UserService
from django.urls import reverse
from django.db import IntegrityError
from loguru import logger


class InstagramService(object):
    client_id = os.environ.get(
        "INSTAGRAM_CLIENT_ID", "f6c17abf61f64a7b9d64f8a0ddabd1b3"
    )
    client_secret = os.environ.get(
        "INSTAGRAM_CLIENT_SECRET", "78697d9c463d48ef81096baee8756c24"
    )

    def __init__(self, **kwargs):
        self.callback = reverse(
            "external_services:instagram-service:callback-instagram-service"
        )

    @classmethod
    def exchange_code_for_access_token(cls, code, redirect_uri, **kwargs):
        url = u"https://api.instagram.com/oauth/access_token"
        data = {
            u"client_id": cls.client_id,
            u"client_secret": cls.client_secret,
            u"code": code,
            u"grant_type": u"authorization_code",
            u"redirect_uri": redirect_uri,
        }

        response = requests.post(url, data=data)

        account_data = json.loads(response.content)

        return account_data

    @staticmethod
    def get_auth_url():
        return reverse("external_services:instagram-service:connect-instagram-service")

    def auth(self, request):
        return self.get_request_token(request)

    def get_request_token(self, request):
        callback = request.build_absolute_uri(self.callback)
        auth_url = (
            "https://api.instagram.com/oauth/authorize/?client_id={client_id}"
            "&redirect_uri={redirect_url}&response_type=code&hl=en".format(
                client_id=self.client_id, redirect_url=callback
            )
        )
        return auth_url

    def callback_oauth1(self, request):
        code = request.GET.get("code")
        callback = request.build_absolute_uri(self.callback)

        data = self.exchange_code_for_access_token(code, callback)

        try:
            service = Services.objects.get(name="Instagram", status=True)
        except Services.DoesNotExist:
            return reverse("external_services:all-external-services")

        try:
            user_service = UserService.objects.get(user=request.user, service=service)
            user_service.auth_token = data.get("access_token")
            user_service.save()
            logger.info("{} created".format(user_service))
        except UserService.DoesNotExist:
            try:
                user_service = UserService.objects.create(
                    user=request.user,
                    service=service,
                    auth_token=data.get("access_token"),
                    refresh_token="",
                    auth_token_secret="",
                )
                logger.info("{} created".format(user_service))
            except IntegrityError as e:
                logger.error(e)

        return reverse("external_services:all-external-services")
