from django.contrib.auth.models import User
from django.test import TestCase
from django.db import IntegrityError
from django.urls import reverse
from user_profile.models import (
    RelationShipProfile,
    FOLLOWING,
    BLOCK,
    LikeProfile,
    Profile,
)
from publications.models import Publication
from django.core.management import call_command


class RelationShipTestClass(TestCase):
    def setUp(self):
        User.objects.create(username="usuario", password="foo")
        User.objects.create(username="usuario2", password="foo")

    def test_create_new_relation_ship(self):
        u = User.objects.get(username="usuario")
        u2 = User.objects.get(username="usuario2")
        rel = RelationShipProfile.objects.create(
            to_profile=u2.profile, from_profile=u.profile, type=FOLLOWING
        )
        self.assertIsNotNone(rel)

    def test_block_user(self):
        u = User.objects.get(username="usuario")
        u2 = User.objects.get(username="usuario2")
        rel = RelationShipProfile.objects.create(
            to_profile=u2.profile, from_profile=u.profile, type=BLOCK
        )
        self.assertIsNotNone(rel)

    def test_create_new_relationship_blocked_user(self):
        u = User.objects.get(username="usuario")
        u2 = User.objects.get(username="usuario2")
        RelationShipProfile.objects.create(
            to_profile=u2.profile, from_profile=u.profile, type=BLOCK
        )
        self.assertRaises(
            IntegrityError,
            RelationShipProfile.objects.create,
            to_profile=u2.profile,
            from_profile=u.profile,
            type=FOLLOWING,
        )

    def test_create_symmetric_relationship(self):
        u = User.objects.get(username="usuario")
        u2 = User.objects.get(username="usuario2")
        rel1 = RelationShipProfile.objects.create(
            to_profile=u2.profile, from_profile=u.profile, type=FOLLOWING
        )
        rel2 = RelationShipProfile.objects.create(
            to_profile=u.profile, from_profile=u2.profile, type=FOLLOWING
        )
        self.assertIsNotNone(rel1)
        self.assertIsNotNone(rel2)


class UserContentTest(TestCase):
    @classmethod
    def setUpTestData(self):
        call_command("badgify_sync", "badges")
        new_user = User.objects.create_user(username="foo", password="foo")
        publications = [
            Publication.objects.create(
                author=new_user, content="FOO", board_owner=new_user
            )
            for x in range(1, 27)
        ]
        for p in publications:
            p.user_give_me_like.add(new_user)

    def test_get_content(self):
        logged_in = self.client.login(username="foo", password="foo")
        self.assertTrue(logged_in)
        response = self.client.get(reverse("user_profile:salad_user_content"))
        self.assertEqual(response.status_code, 200)

    def test_get_content_no_login(self):
        response = self.client.get(reverse("user_profile:salad_user_content"))
        self.assertEqual(response.status_code, 302)

    def test_get_content_pagination(self):
        logged_in = self.client.login(username="foo", password="foo")
        self.assertTrue(logged_in)
        response = self.client.get(reverse("user_profile:salad_user_content"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["mixed"]), 25)

    def test_get_content_pagination_page_2(self):
        logged_in = self.client.login(username="foo", password="foo")
        self.assertTrue(logged_in)
        url = "{0}?page={1}".format(reverse("user_profile:salad_user_content"), 2)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["mixed"]), 1)


class UserLikeTest(TestCase):
    def setUp(self):
        user_1 = User.objects.create_user(username="foo1", password="foo")
        user_2 = User.objects.create_user(username="foo2", password="foo2")
        self.assertIsNotNone(user_1)
        self.assertIsNotNone(user_2)
        self.assertIsNotNone(user_1.profile)
        self.assertIsNotNone(user_2.profile)

    def test_like_user(self):
        profile_1 = Profile.objects.get(user__username="foo1")
        profile_2 = Profile.objects.get(user__username="foo2")

        self.assertIsNotNone(profile_1)
        self.assertIsNotNone(profile_2)

        like = LikeProfile.objects.create(to_profile=profile_1, from_profile=profile_2)
        self.assertIsNotNone(like)
        self.assertEqual(like.to_profile, profile_1)
        self.assertEqual(like.from_profile, profile_2)
