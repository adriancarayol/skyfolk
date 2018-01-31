from django.contrib.auth.decorators import login_required
from django.db import IntegrityError

from dash.contrib.plugins.poll.models import PollResponse
from .forms import PollResponseForm
from django.http import JsonResponse


@login_required
def submit_poll_response(request):
    form = PollResponseForm(request.POST)
    valid_form = False
    options = False
    if request.POST:
        if form.is_valid():
            poll_id = form.cleaned_data['pk']
            if '_positive' in request.POST:
                options = True
                valid_form = True
            elif '_negative' in request.POST:
                options = False
                valid_form = True

            try:
                exists = PollResponse.objects.filter(poll_id=poll_id, user=request.user).exists()
                # Cambiar respuesta del usuario
                if exists:
                    PollResponse.objects.filter(poll_id=poll_id, user=request.user).update(options=options)
                else:
                    PollResponse.objects.create(poll_id=poll_id, user=request.user, options=options)
            except IntegrityError:
                valid_form = False

    return JsonResponse({'response': valid_form})
