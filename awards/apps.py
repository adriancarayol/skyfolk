from django.apps import AppConfig


class AwardsConfiguration(AppConfig):
    name = 'awards'

    def ready(self):
        super(AwardsConfiguration, self).ready()
        import awards.signals
