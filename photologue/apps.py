from django.apps import AppConfig


class Config(AppConfig):
    name = "photologue"

    def ready(self):
        super(Config, self).ready()
        import photologue.signals
