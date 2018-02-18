import numpy as np
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
    data = {
        'response': valid_form,
    }

    if request.POST:
        if form.is_valid():
            poll_id = form.cleaned_data['pk']
            if '_positive' == request.POST.get('submit', None):
                options = True
                valid_form = True
            elif '_negative' == request.POST.get('submit', None):
                options = False
                valid_form = True

            if valid_form:
                try:
                    exists = PollResponse.objects.filter(poll_id=poll_id, user=request.user).exists()
                    # Cambiar respuesta del usuario
                    if exists:
                        PollResponse.objects.filter(poll_id=poll_id, user=request.user).update(options=options)
                    else:
                        PollResponse.objects.create(poll_id=poll_id, user=request.user, options=options)
                except (IntegrityError, PollResponse.DoestNotExist) as e:
                    valid_form = False

            if valid_form:
                poll_responses = PollResponse.objects.filter(poll_id=poll_id).values_list('options', flat=True)
                value_of_no = np.size(poll_responses) - np.count_nonzero(poll_responses)
                value_of_yes = np.count_nonzero(poll_responses)

                data['response'] = valid_form,
                data['option'] = options
                data['value_of_no'] = value_of_no,
                data['value_of_yes'] = value_of_yes

    return JsonResponse(data)
