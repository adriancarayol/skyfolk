from django.db import models
from django.contrib.auth.models import User


class Services(models.Model):
    name = models.CharField(max_length=255)
    status = models.BooleanField(default=False)
    description = models.CharField(max_length=255)
    
    
class UserService(models.Model):
    service = models.ForeignKey(Services, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    auth_token = models.CharField(max_length=255)
    auth_token_secret = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255, default='')

    class Meta:
        unique_together = ('service', 'user')

    def __str__(self):
        return self.service.name
