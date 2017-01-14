from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .models import SupportPasswordModel
from django.views.generic.edit import FormView
from .forms import SupportPasswordForm
from utils.ajaxable_reponse_mixin import AjaxableResponseMixin
from django.utils.translation import ugettext_lazy as _


class SupportPasswordView(FormView, AjaxableResponseMixin):
    """
    Vista para contactar con el soporte
    cuando el usuario tiene problemas con su
    password.
    """
    template_name = "support/password-contact.html"
    form_class = SupportPasswordForm
    success_url = '/'

    def form_valid(self, form):
        obj = form.save(commit=False)
        user = form.clean_username_or_email()
        if user is not False:
            obj.user = user
        obj.save()
        form.send_email(obj.title, obj.description, obj.user.email)
        return super(SupportPasswordView, self).form_valid(form)

support_view = SupportPasswordView.as_view()