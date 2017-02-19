# from django.shortcuts import render

from django.shortcuts import render_to_response
from django.template import RequestContext


# from django.utils import simplejson
def landing(request):
    return render_to_response(
        "account/base.html",
        RequestContext(request)
    )
