from django.apps import AppConfig


class TimelineAppConfiguration(AppConfig):
    name = 'timeline'

    def ready(self):
        super(TimelineAppConfiguration, self).ready()
        import timeline.signals
