from django.views import View
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from external_services.youtube.youtube_service import YouTubeService


class AuthYouTubeServiceView(View):
    def get(self, request, *args, **kwargs):
        youtube_service = YouTubeService()
        return redirect(youtube_service.auth(request))


class CreateYouTubeServiceView(View):
    def get(self, request, *args, **kwargs):
        youtube_service = YouTubeService()
        return redirect(youtube_service.callback_oauth1(request))


auth_youtube_view = login_required(AuthYouTubeServiceView.as_view())
create_youtube_service_view = login_required(CreateYouTubeServiceView.as_view())
