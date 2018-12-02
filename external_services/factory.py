from external_services.twitter.forms import CreateNewTwitterWidgetForm
from external_services.instagram.forms import CreateNewInstagramWidgetForm
from external_services.youtube.forms import CreateNewYoutubeWidgetForm


class ServiceFormFactory(object):

    @staticmethod
    def factory(service_name):
        if not service_name:
            raise ValueError('Service name cannot be empty or None')

        if service_name == 'twitter':
            return CreateNewTwitterWidgetForm

        if service_name == 'instagram':
            return CreateNewInstagramWidgetForm

        if service_name == 'youtube':
            return CreateNewYoutubeWidgetForm

        raise ValueError('Unknown service name')
