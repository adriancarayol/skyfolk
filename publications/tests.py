from django.test import TestCase
from neomodel import db, clear_neo4j_database
from django.contrib.auth.models import User
from publications.models import Publication
from django.core.urlresolvers import reverse

class PublicationTest(TestCase):
    @classmethod
    def setUpTestData(self):
        clear_neo4j_database(db)
        User.objects.create_user(username='foo', password='foo')

    def test_create_publication(self):
        user = User.objects.get(username='foo')
        self.assertIsNotNone(user)
        p = Publication.objects.create(author=user, board_owner=user, content='foo')
        self.assertIsNotNone(p)

    def test_create_view_publication(self):
        self.assertTrue(self.client.login(username='foo', password='foo'))
        board_owner = User.objects.get(username='foo')
        self.assertIsNotNone(board_owner)

        response = self.client.post(reverse('publications:new_publication'), {'content': 'foo', 'board_owner': board_owner.id})
        self.assertEqual(response.status_code, 200)

    def test_create_view_without_content(self):
        self.assertTrue(self.client.login(username='foo', password='foo'))
        board_owner = User.objects.get(username='foo')
        self.assertIsNotNone(board_owner)

        response = self.client.post(reverse('publications:new_publication'), {'board_owner': board_owner.id})
        self.assertEqual(response.status_code, 200)
