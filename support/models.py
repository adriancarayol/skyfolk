# encoding:utf-8
from django.db import models
from django.contrib.auth.models import User


class SupportPasswordModel(models.Model):
    """
    Clase para almacenar una peticion de
    ayuda por parte del usuario.
    Por ejemplo, el usuario tiene problemas para restablecer
    su password.
    """
    user = models.ForeignKey(User)
    title = models.CharField(max_length=128, blank=False, null=False)
    description = models.TextField(max_length=2048, blank=False, null=False)