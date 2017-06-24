from django.test import TestCase
from django.contrib.auth.models import User
from .models import Publication, ExtraContent
from neomodel import clear_neo4j_database
from neomodel import db


class PublicationTestCase(TestCase):
    def setUp(self):
        clear_neo4j_database(db)
        u = User.objects.create(username="example", password="foo")
        User.objects.create(username="example_2", password="foo_2")
        Publication.objects.create(content='example_content', author=u, board_owner=u)

    def test_parse_content(self):
        pub = Publication.objects.get(author__username='example')
        self.assertIsNotNone(pub, pub.content)

    def test_extra_content(self):
        pub = Publication.objects.filter(author__username="example").first()
        e = ExtraContent.objects.create(pub=pub, title="Extra content example")
        self.assertIsNotNone(e)

    def test_like_publication(self):
        pub = Publication.objects.filter(author__username="example").first()
        u2 = User.objects.get(username="example_2")
        pub.user_give_me_like.add(u2)
        pub.liked += 1
        self.assertEqual(len(pub.user_give_me_like.all()), pub.liked)

    def test_hate_publication(self):
        pub = Publication.objects.filter(author__username="example").first()
        u2 = User.objects.get(username="example_2")
        pub.user_give_me_hate.add(u2)
        pub.hated += 1
        self.assertEqual(len(pub.user_give_me_hate.all()), pub.hated)