from django.apps import AppConfig


class UserGuideConfig(AppConfig):
    name = "user_guide"
    verbose_name = "Django User Guide"

    def ready(self):
        from .models import create_user_guides

        create_user_guides()
