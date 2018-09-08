# -*- coding: utf-8 -*-
import badgify
import os
from badgify.recipe import BaseRecipe
from django.conf import settings
from django.contrib.auth.models import User


class FirstLoginRecipe(BaseRecipe):
    """
    First login badge
    """
    name = '¡Todo tiene un inicio!'
    slug = 'new-account'
    description = '¡Bienvenido a Skyfolk! - Has obtenido este logro al registrarte exitosamente.'
    points = 5
    category = 'hero'

    @property
    def image(self):
        return os.path.join(settings.STATIC_URL, 'badges/ic_pets_black_24dp_2x.png')

    @property
    def user_ids(self):
        return User.objects.filter(is_active=True).values_list('id', flat=True)


class TenPubsReachedRecipe(BaseRecipe):
    """
    Ten publications reached badge
    """
    name = '¡10 publicaciones realizadas!'
    slug = '10-pubs-reached'
    description = 'Has obtenido este logro por realizar 10 publicaciones en Skyfolk.'
    points = 25
    category = 'writer'

    @property
    def image(self):
        return os.path.join(settings.STATIC_URL, 'badges/ic_comment_black_24dp_2x.png')

    @property
    def user_ids(self):
        return User.objects.filter(is_active=True).values_list('id', flat=True)


class FirstPublicationRecipe(BaseRecipe):
    """
    First publication badge
    """
    name = '¡Primera publicación!'
    slug = 'first-publication'
    description = 'Has obtenido este logro por realizar tu primera publicación en Skyfolk.'
    points = 5
    category = 'writer'

    @property
    def image(self):
        return os.path.join(settings.STATIC_URL, 'badges/ic_comment_black_24dp_2x.png')

    @property
    def user_ids(self):
        return User.objects.filter(is_active=True).values_list('id', flat=True)


class FirstDirectMessageRecipe(BaseRecipe):
    """
    First publication badge
    """
    name = 'Tu primer mensaje privado'
    slug = 'first-direct-message'
    description = 'Has obtenido este logro por realizar tu primer mensaje privado en Skyfolk.'
    points = 25
    category = 'hero'

    @property
    def image(self):
        return os.path.join(settings.STATIC_URL, 'badges/outline_mail_outline_black_18dp.png')

    @property
    def user_ids(self):
        return User.objects.filter(is_active=True).values_list('id', flat=True)


class FirstMediaRecipe(BaseRecipe):
    """
    First publication badge
    """
    name = 'Tu primera subida'
    slug = 'first-upload-media'
    description = 'Has obtenido este logro por subir una imagen o un vídeo a Skyfolk.'
    points = 25
    category = 'hero'

    @property
    def image(self):
        return os.path.join(settings.STATIC_URL, 'badges/baseline_cloud_upload_black_18dp.png')

    @property
    def user_ids(self):
        return User.objects.filter(is_active=True).values_list('id', flat=True)


class CasanovaRecipe(BaseRecipe):
    """
    Casanova badge
    """
    name = 'Casanova'
    slug = 'casanova-recipe'
    description = 'Has obtenido este logro por subir recibir 100 me gusta a tu perfil en Skyfolk.'
    points = 15
    category = 'star'

    @property
    def image(self):
        return os.path.join(settings.STATIC_URL, 'badges/casanova.png')

    @property
    def user_ids(self):
        return User.objects.filter(is_active=True).values_list('id', flat=True)


class DonJuanRecipe(BaseRecipe):
    """
    Don juan badge
    """
    name = 'Don Juan'
    slug = 'don-juan-recipe'
    description = 'Has obtenido este logro por subir recibir 5000 me gusta a tu perfil en Skyfolk.'
    points = 100
    category = 'star'

    @property
    def image(self):
        return os.path.join(settings.STATIC_URL, 'badges/baseline_star_half_black_18dp.png')

    @property
    def user_ids(self):
        return User.objects.filter(is_active=True).values_list('id', flat=True)


class InfluencerRecipe(BaseRecipe):
    """
    Influencer badge
    """
    name = 'Influencer'
    slug = 'influencer-recipe'
    description = 'Has obtenido este logro por subir recibir 150000 me gusta a tu perfil en Skyfolk.'
    points = 150
    category = 'star'

    @property
    def image(self):
        return os.path.join(settings.STATIC_URL, 'badges/baseline_star_black_18dp.png')

    @property
    def user_ids(self):
        return User.objects.filter(is_active=True).values_list('id', flat=True)


class EditorRecipe(BaseRecipe):
    """
    Editor badge
    """
    name = 'Editor'
    slug = 'editor-recipe'
    description = 'Has obtenido este logro por subir recibir 100 me gusta a tus publicaciones en Skyfolk.'
    points = 15
    category = 'writer'

    @property
    def image(self):
        return os.path.join(settings.STATIC_URL, 'badges/baseline_star_black_18dp.png')

    @property
    def user_ids(self):
        return User.objects.filter(is_active=True).values_list('id', flat=True)


class PulitzerRecipe(BaseRecipe):
    """
    Editor badge
    """
    name = 'Pulitzer'
    slug = 'pulitzer-recipe'
    description = 'Has obtenido este logro por subir recibir 5000 me gusta a tus publicaciones en Skyfolk.'
    points = 100
    category = 'writer'

    @property
    def image(self):
        return os.path.join(settings.STATIC_URL, 'badges/baseline_thumb_up_black_18dp.png')

    @property
    def user_ids(self):
        return User.objects.filter(is_active=True).values_list('id', flat=True)


badgify.register(FirstLoginRecipe)
badgify.register(FirstPublicationRecipe)
badgify.register(FirstDirectMessageRecipe)
badgify.register(FirstMediaRecipe)
badgify.register(TenPubsReachedRecipe)
badgify.register(CasanovaRecipe)
badgify.register(DonJuanRecipe)
badgify.register(InfluencerRecipe)
badgify.register(EditorRecipe)
badgify.register(PulitzerRecipe)
