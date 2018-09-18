from datetime import datetime, timedelta

from django.conf import settings
from django.contrib import auth


class AutoLogout:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if not request.user.is_authenticated:
            return response

        try:
            if datetime.now() - request.session['last_touch'] > timedelta(0, settings.AUTO_LOGOUT_DELAY * 60, 0):
                auth.logout(request)
                del request.session['last_touch']
        except KeyError:
            pass

        request.session['last_touch'] = datetime.now()

        return response
