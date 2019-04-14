from django.contrib.auth.models import User
from django.test import TestCase

from user_groups.models import UserGroups
from .models import PublicationGroup, ExtraGroupContent


class PublicationGroupTestCase(TestCase):
    def setUp(self):
        u = User.objects.create(username="test", password="testcreate")
        g = UserGroups.objects.create(name="test", description="test", owner=u)
        PublicationGroup.objects.create(author=u, board_group=g, content="YEE")

    def test_create_publication(self):
        u = User.objects.get(username="test")
        g = UserGroups.objects.get(name="test", description="test", owner=u)
        p = PublicationGroup.objects.get(author=u, board_group=g)
        self.assertIsNotNone(p)

    def test_parse_content(self):
        pub = PublicationGroup.objects.get(author__username="test")
        pub.parse_content()
        self.assertIsNotNone(pub, pub.content)

    def test_extra_content(self):
        pub = PublicationGroup.objects.filter(author__username="test").first()
        e = ExtraGroupContent.objects.create(
            publication=pub, title="Extra content example"
        )
        self.assertIsNotNone(e)

    def test_like_publication(self):
        pub = PublicationGroup.objects.filter(author__username="test").first()
        u2 = User.objects.get(username="test")
        pub.user_give_me_like.add(u2)
        self.assertIn(u2, pub.user_give_me_like.all())

    def test_hate_publication(self):
        pub = PublicationGroup.objects.filter(author__username="test").first()
        u2 = User.objects.get(username="test")
        pub.user_give_me_hate.add(u2)
        self.assertIn(u2, pub.user_give_me_hate.all())

    def test_add_mention(self):
        pub = PublicationGroup.objects.filter(author__username="test").first()
        content = "Hola @example_2"
        pub.content = content
        pub.parse_mentions()
        pub.save()
        content_parse = 'Hola<a href="/profile/example_2">@example_2</a>'
        self.assertHTMLEqual(content_parse, pub.content)

    def test_delete_extra_content(self):
        pub = PublicationGroup.objects.filter(author__username="test").first()
        ExtraGroupContent.objects.create(publication=pub, title="Extra content example")
        pub.delete()
        self.assertFalse(ExtraGroupContent.objects.filter(publication=pub).exists())
