# -*- coding: utf-8 -*-
import badgify
import os
from badgify.recipe import BaseRecipe
from django.conf import settings
from django.contrib.auth.models import User


class FirstLoginRecipe(BaseRecipe):
    """
    People loving Python.
    """
    name = '¡Todo tiene un inicio!'
    slug = 'new-account'
    description = '¡Bienvenido a Skyfolk! - Has obtenido este logro al registrarte exitosamente.'
    points = 5
    
    @property
    def image(self):
        return os.path.join(settings.STATIC_URL, 'badges/ic_pets_black_24dp_2x.png') 

    @property
    def user_ids(self):
        return User.objects.filter(is_active=True).values_list('id', flat=True)


class TenPubsReachedRecipe(BaseRecipe):
    """
    People loving JS.
    """
    name = '¡10 publicaciones realizadas!'
    slug = '10-pubs-reached'
    description = 'Has obtenido este logro por realizar 10 publicaciones en Skyfolk.'
    points = 10

    @property
    def image(self):
        return os.path.join(settings.STATIC_URL, 'badges/ic_comment_black_24dp_2x.png')

    @property
    def user_ids(self):
        return User.objects.filter(is_active=True).values_list('id', flat=True)


badgify.register(FirstLoginRecipe)
badgify.register(TenPubsReachedRecipe)