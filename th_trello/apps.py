from django.apps import AppConfig


class ThTrelloAppConfiguration(AppConfig):
    name = 'th_trello'

    def ready(self):
        super(ThTrelloAppConfiguration, self).ready()
