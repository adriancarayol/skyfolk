from django.db.models import Q
from django.test import TestCase
from django.contrib.auth.models import User
from user_profile.models import RelationShipProfile, FOLLOWING, BLOCK
from publications.models import Publication


class NewTestClass(TestCase):
    def setUp(self):
        User.objects.create(username="usuario", password="foo")
        User.objects.create(username="usuario2", password="foo")

    def test_get_following_publications(self):
        u = User.objects.get(username="usuario")
        u2 = User.objects.get(username="usuario2")
        RelationShipProfile.objects.create(to_profile=u2.profile, from_profile=u.profile, type=FOLLOWING)
        following = RelationShipProfile.objects.filter(Q(from_profile=u.profile) & ~Q(type=BLOCK)).values(
            'to_profile_id')
        self.assertTrue(Publication.objects.filter(author__profile__in=following).exists())

    def test_get_not_blocked_publications(self):
        u = User.objects.get(username="usuario")
        u2 = User.objects.get(username="usuario2")
        RelationShipProfile.objects.create(to_profile=u2.profile, from_profile=u.profile, type=BLOCK)
        users_not_blocked_me = RelationShipProfile.objects.filter(
            to_profile=u.profile, type=BLOCK).values('from_profile_id')
        self.assertFalse(Publication.objects.exclude(author__profile__in=users_not_blocked_me).exists())

    def test_get_following_board_publications(self):
        u = User.objects.get(username="usuario")
        u2 = User.objects.get(username="usuario2")
        RelationShipProfile.objects.create(to_profile=u2.profile, from_profile=u.profile, type=FOLLOWING)
        following = RelationShipProfile.objects.filter(Q(from_profile=u.profile) & ~Q(type=BLOCK)).values(
            'to_profile_id')
        self.assertTrue(Publication.objects.filter(board_owner__profile__in=following).exists())

    def test_get_not_blocked_board_publications(self):
        u = User.objects.get(username="usuario")
        u2 = User.objects.get(username="usuario2")
        RelationShipProfile.objects.create(to_profile=u2.profile, from_profile=u.profile, type=BLOCK)
        users_not_blocked_me = RelationShipProfile.objects.filter(
            to_profile=u.profile, type=BLOCK).values('from_profile_id')
        self.assertFalse(Publication.objects.exclude(board_owner__profile__in=users_not_blocked_me).exists())
