from django.views import View
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from external_services.twitter.twitter_service import TwitterService


class AuthTwitterServiceView(View):
    def get(self, request, *args, **kwargs):
        twitter_service = TwitterService()
        return redirect(twitter_service.auth(request))
    

class CreateTwitterServiceView(View):
    def get(self, request, *args, **kwargs):
        twitter_service = TwitterService()
        return redirect(twitter_service.callback_oauth1(request))

auth_twitter_view = login_required(AuthTwitterServiceView.as_view())
create_twitter_service_view = login_required(CreateTwitterServiceView.as_view())