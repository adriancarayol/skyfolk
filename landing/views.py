# from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
#from django.utils import simplejson
import json
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist


def landing(request):
    return render_to_response(
        "account/base.html",
        RequestContext(request)
    )

