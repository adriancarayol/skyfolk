from django.contrib.auth.models import User
from django.test import TestCase
from neomodel import clear_neo4j_database
from neomodel import db

from .models import Publication, ExtraContent


class PublicationTestCase(TestCase):
    def setUp(self):
        clear_neo4j_database(db)
        u = User.objects.create(username="example", password="foo")
        User.objects.create(username="example_2", password="foo_2")
        Publication.objects.create(content='example_content', author=u, board_owner=u)

    def test_parse_content(self):
        pub = Publication.objects.get(author__username='example')
        pub.parse_content()
        self.assertIsNotNone(pub, pub.content)

    def test_extra_content(self):
        pub = Publication.objects.filter(author__username="example").first()
        e = ExtraContent.objects.create(publication=pub, title="Extra content example")
        self.assertIsNotNone(e)

    def test_like_publication(self):
        pub = Publication.objects.filter(author__username="example").first()
        u2 = User.objects.get(username="example_2")
        pub.user_give_me_like.add(u2)
        self.assertIn(u2, pub.user_give_me_like.all())

    def test_hate_publication(self):
        pub = Publication.objects.filter(author__username="example").first()
        u2 = User.objects.get(username="example_2")
        pub.user_give_me_hate.add(u2)
        self.assertIn(u2, pub.user_give_me_hate.all())

    def test_add_mention(self):
        pub = Publication.objects.filter(author__username="example").first()
        content = "Hola @example_2"
        pub.content = content
        pub.parse_mentions()
        pub.save()
        content_parse = 'Hola<a href="/profile/example_2">@example_2</a>'
        self.assertHTMLEqual(content_parse, pub.content)

    def test_delete_extra_content(self):
        pub = Publication.objects.filter(author__username="example").first()
        ExtraContent.objects.create(publication=pub, title="Extra content example")
        pub.delete()
        self.assertFalse(ExtraContent.objects.filter(publication=pub).exists())
