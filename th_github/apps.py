from django.apps import AppConfig


class ThGithubAppConfiguration(AppConfig):
    name = 'th_github'

    def ready(self):
        super(ThGithubAppConfiguration, self).ready()
