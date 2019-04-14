from django.apps import AppConfig


class GroupAppConfiguration(AppConfig):
    name = "user_groups"

    def ready(self):
        import user_groups.signals

        super(GroupAppConfiguration, self).ready()
