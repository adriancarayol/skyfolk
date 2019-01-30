import os
import google_auth_oauthlib.flow
from external_services.models import Services, UserService
from django.urls import reverse
from django.db import IntegrityError
from django.conf import settings

CLIENT_SECRETS_FILE = os.path.join(settings.BASE_DIR, "client_secret.json")
print(CLIENT_SECRETS_FILE)


class YouTubeService(object):
    scopes = ['https://www.googleapis.com/auth/youtube.force-ssl',
              'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile']
    api_service_name = 'youtube'
    api_version = 'v3'

    def __init__(self, **kwargs):
        self.callback = reverse('external_services:youtube-service:callback-youtube-service')

    @staticmethod
    def get_auth_url():
        return reverse('external_services:youtube-service:connect-youtube-service')

    def auth(self, request):
        return self.get_request_token(request)

    def get_request_token(self, request):
        callback = request.build_absolute_uri(self.callback)
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, scopes=self.scopes)
        flow.redirect_uri = callback
        authorization_url, state = flow.authorization_url(
            # This parameter enables offline access which gives your application
            # both an access and refresh token.
            access_type='offline',
            # This parameter enables incremental auth.
            include_granted_scopes='true')

        request.session['request_token'] = state
        return authorization_url

    def callback_oauth1(self, request):
        callback = request.build_absolute_uri(self.callback)
        state = request.session['request_token']
        del request.session['request_token']

        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, scopes=self.scopes, state=state)

        flow.redirect_uri = callback
        authorization_response = request.build_absolute_uri()
        flow.fetch_token(authorization_response=authorization_response)
        credentials = flow.credentials

        try:
            service = Services.objects.get(name="YouTube", status=True)
        except Services.DoesNotExist:
            return reverse('external_services:all-external-services')

        try:
            user_service = UserService.objects.get(user=request.user, service=service)
            user_service.auth_token = credentials.token
            user_service.refresh_token = credentials.refresh_token
            user_service.save()
        except UserService.DoesNotExist as e:
            try:
                UserService.objects.create(user=request.user, service=service,
                                           auth_token=credentials.token,
                                           refresh_token=credentials.refresh_token,
                                           auth_token_secret='')
            except IntegrityError as e:
                pass

        return reverse('external_services:all-external-services')
