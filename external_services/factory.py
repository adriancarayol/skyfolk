from external_services.twitter.forms import CreateNewTwitterWidgetForm


class ServiceFormFactory(object):

    @staticmethod
    def factory(service_name):
        if not service_name:
            raise ValueError('Service name cannot be empty or None')

        if service_name == 'twitter':
            return CreateNewTwitterWidgetForm

        raise ValueError('Unknown service name')
