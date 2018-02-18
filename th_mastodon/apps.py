from django.apps import AppConfig


class ThMastodonAppConfiguration(AppConfig):
    name = 'th_mastodon'

    def ready(self):
        super(ThMastodonAppConfiguration, self).ready()
