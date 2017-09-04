from django.contrib.auth.models import User
from django.test import TestCase

from user_groups.models import UserGroups
from .models import PublicationGroup


class PublicationGroupTestCase(TestCase):
    def setUp(self):
        u = User.objects.create(username="test", password="testcreate")
        UserGroups.objects.create(name="test", description="test",
                owner=u)

    def test_create_publication(self):
        u = User.objects.get(username="test")
        g = UserGroups.objects.get(name="test")
        p = PublicationGroup.objects.create(author=u, board_group=g)
        self.assertIsNotNone(p)
