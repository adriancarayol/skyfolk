from django.apps import AppConfig


class ThBulletAppConfiguration(AppConfig):
    name = 'th_services.th_pushbullet'

    def ready(self):
        super(ThBulletAppConfiguration, self).ready()
