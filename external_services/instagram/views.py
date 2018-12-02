from django.views import View
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from external_services.instagram.instagram_service import InstagramService


class AuthInstagramServiceView(View):
    def get(self, request, *args, **kwargs):
        instagram_service = InstagramService()
        return redirect(instagram_service.auth(request))


class CreateInstagramServiceView(View):
    def get(self, request, *args, **kwargs):
        instagram_service = InstagramService()
        return redirect(instagram_service.callback_oauth1(request))


auth_instagram_view = login_required(AuthInstagramServiceView.as_view())
create_instagram_service_view = login_required(CreateInstagramServiceView.as_view())
