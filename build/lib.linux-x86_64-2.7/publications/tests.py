from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase
from neomodel import db, clear_neo4j_database

from publications.models import Publication


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

        response = self.client.post(reverse('publications:new_publication'),
                                    {'content': 'foo', 'board_owner': board_owner.id})

        self.assertIsNotNone(Publication.objects.get(content='foo', board_owner=board_owner.id))
        self.assertEqual(response.status_code, 200)

    def test_create_view_without_content(self):
        self.assertTrue(self.client.login(username='foo', password='foo'))
        board_owner = User.objects.get(username='foo')
        self.assertIsNotNone(board_owner)

        response = self.client.post(reverse('publications:new_publication'), {'board_owner': board_owner.id})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Publication.objects.filter(content='foo', board_owner=board_owner.id).exists())

    def test_create_view_without_board_owner(self):
        self.assertTrue(self.client.login(username='foo', password='foo'))

        response = self.client.post(reverse('publications:new_publication'), {'content': 'pol'})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Publication.objects.filter(content='pol').exists())

    def tearDown(self):
        clear_neo4j_database(db)
