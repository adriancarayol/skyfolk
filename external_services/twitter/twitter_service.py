import os
import tweepy
from external_services.models import Services, UserService
from django.urls import reverse
from django.db import IntegrityError


class TwitterService(object):
    def __init__(self, **kwargs):
        self.consumer_token = os.environ.get(
            "TWITTER_CONSUMER_TOKEN", "ICxk7pSKDmUffHxEVyP2bqQ2l"
        )
        self.consumer_secret = os.environ.get(
            "TWITTER_CONSUMER_SECRET",
            "ptzwzgTHzR0jj2jrvibTgKnFTuPdICY2HBUeVCAgiTHREa2evR",
        )
        self.callback = reverse(
            "external_services:twitter-service:callback-twitter-service"
        )

    @staticmethod
    def get_auth_url():
        return reverse("external_services:twitter-service:connect-twitter-service")

    def auth(self, request):
        return self.get_request_token(request)

    def get_request_token(self, request):
        auth = tweepy.OAuthHandler(self.consumer_token, self.consumer_secret)
        redirect_url = auth.get_authorization_url()
        request.session["request_token"] = auth.request_token
        return redirect_url

    def callback_oauth1(self, request):
        request_token = request.session["request_token"]
        del request.session["request_token"]

        auth = tweepy.OAuthHandler(
            self.consumer_token, self.consumer_secret, self.callback
        )
        auth.request_token = request_token

        verifier = request.GET.get("oauth_verifier")
        auth.get_access_token(verifier)

        try:
            service = Services.objects.get(name="Twitter", status=True)
        except Services.DoesNotExist:
            return reverse("external_services:all-external-services")

        try:
            user_service = UserService.objects.get(user=request.user, service=service)
            user_service.auth_token = auth.access_token
            user_service.auth_token_secret = auth.access_token_secret
            user_service.save()
        except UserService.DoesNotExist as e:
            try:
                UserService.objects.create(
                    user=request.user,
                    service=service,
                    auth_token=auth.access_token,
                    auth_token_secret=auth.access_token_secret,
                )
            except IntegrityError as e:
                pass

        return reverse("external_services:all-external-services")
