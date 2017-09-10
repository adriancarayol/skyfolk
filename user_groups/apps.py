from django.apps import AppConfig


class GroupAppConfiguration(AppConfig):
    name = 'user_groups'

    def ready(self):
        super(GroupAppConfiguration, self).ready()
        import user_groups.signals
