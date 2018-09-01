from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from feedback.forms import ContactForm


class FeedbackView(FormView):
    template_name = 'feedback/feedback.html'
    success_url = '/feedback/success/'
    form_class = ContactForm

    def form_valid(self, form):
        form.save()
        form.send_email()
        return super().form_valid(form)


class FeedbackSuccess(TemplateView):
    template_name = 'feedback/success.html'
