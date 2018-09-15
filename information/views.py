from django.views.generic import TemplateView


class PolicyPrivacyView(TemplateView):
    template_name = "information/privacy_policy.html"
