# -*- coding: utf-8 -*-

import sys

import user_profile
from avatar.models import Avatar

if sys.version > '3':
    long = int


def slug2id(slug):
    return long(slug) - 110909


def id2slug(id):
    return id + 110909


def get_author_avatar(authorpk):
    """
    Devuelve el avatar del autor de la publicacion pasada como parametro
    """
    try:
        avatars = Avatar.objects.get(user=authorpk, primary=True)
    except Avatar.DoesNotExist:
        avatars = None

    if avatars:
        return avatars.get_absolute_url()
    else:
        return user_profile.models.Profile.nodes.get(user_id=authorpk).gravatar
