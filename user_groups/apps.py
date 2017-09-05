from django.apps import AppConfig


class GroupAppConfiguration(AppConfig):
    name = 'user_groups'

    def ready(self):
        super(GroupAppConfiguration, self).ready()
        from user_groups import signals
