from django.apps import AppConfig


class AwardsConfiguration(AppConfig):
    name = 'awards'

    def ready(self):
        super(AwardsConfiguration, self).ready()
        from awards import signals
