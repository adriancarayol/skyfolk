from django.http import JsonResponse


class AjaxableResponseMixin(object):
    """
    Mixin to add AJAX support to a form.
    Must be used with an object-based FormView (e.g. CreateView)
    Extracted from: https://docs.djangoproject.com/es/1.9/topics/class-based-
    views/generic-editing/
    """

    def form_invalid(self, form, errors=None):
        response = super(AjaxableResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            if not errors:
                data = {
                        'error': [u'No hemos podido procesar tu petición.'],
                        'type_error': 'incorret_data',
                }
            else:
                data = {
                    'error': list(errors) if errors else [u'Comprueba el contenido de tu publicación.'],
                    'type_error': 'incorrent_data'
                }
            return JsonResponse(data, status=400)
        else:
            return response

    def form_valid(self, form, msg=None):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        response = super(AjaxableResponseMixin, self).form_valid(form)
        if self.request.is_ajax():
            data = {
                'msg': msg,
                'response': True,
            }
            return JsonResponse(data)
        else:
            return response
