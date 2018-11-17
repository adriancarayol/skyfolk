from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from utils.ajaxable_reponse_mixin import AjaxableResponseMixin
from .forms import SupportPasswordForm
from django.db.models import Q
from django.urls import reverse_lazy


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
        username_or_email = form.cleaned_data['username_or_email']

        try:
            user = User.objects.get(Q(username__iexact=username_or_email) | Q(email=username_or_email))
        except ObjectDoesNotExist:
            form.add_error('username_or_email', 'No hay ninguna cuenta asociada a ese nombre de usuario o email')
            return super().form_invalid(form)

        obj.user = user
        obj.save()

        form.send_email(obj.title, obj.description, obj.user.email)
        return super(SupportPasswordView, self).form_valid(form)

    def get_success_url(self, **kwargs):
        return reverse_lazy('support:support-password-submitted')


class AfterSubmitSupportPasswordView(TemplateView):
    template_name = 'support/submitted_form.html'


support_view = SupportPasswordView.as_view()
after_submit_view = AfterSubmitSupportPasswordView.as_view()