from django.apps import AppConfig


class ThTodoistAppConfiguration(AppConfig):
    name = 'th_todoist'

    def ready(self):
        super(ThTodoistAppConfiguration, self).ready()
