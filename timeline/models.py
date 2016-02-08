from django.db import models

from user_profile.models import UserProfile


class Timeline(models.Model):
    content = models.TextField(blank=False)
    author = models.ForeignKey(UserProfile, related_name='from_timeline')
    profile = models.ForeignKey(UserProfile, related_name='to_timeline')
    insertion_date = models.DateField(auto_now_add=True)


    # Mostrar contenido en formato string.
    def __str__(self):
        return self.content
