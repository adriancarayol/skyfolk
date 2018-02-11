from django.apps import AppConfig


class DashConfiguration(AppConfig):
    name = 'dash'

    def ready(self):
        super(DashConfiguration, self).ready()
        import dash.signals
