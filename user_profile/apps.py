from django.apps import AppConfig


class UserProfileAppConfiguration(AppConfig):
    name = 'user_profile'

    def ready(self):
        super(UserProfileAppConfiguration, self).ready()
        from user_groups import signals
