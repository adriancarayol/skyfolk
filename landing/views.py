# from django.shortcuts import render
import json

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import ensure_csrf_cookie


#from django.utils import simplejson
def landing(request):
    return render_to_response(
        "account/base.html",
        RequestContext(request)
    )

