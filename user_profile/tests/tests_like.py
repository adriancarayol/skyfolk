from django.test import TestCase
from neomodel import db, clear_neo4j_database
from ..models import LikeProfile
from ..node_models import NodeProfile
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse


class LikeProfileTest(TestCase):
    def setUp(self):
        clear_neo4j_database(db)
        User.objects.create_user(username='user1', password='password')
        User.objects.create_user(username='user2', password='password')

    def test_like_profile(self):
        user_1 = User.objects.get(username='user1')
        user_2 = User.objects.get(username='user2')
        node_1 = NodeProfile.nodes.get(user_id=user_1.id)
        node_2 = NodeProfile.nodes.get(user_id=user_2.id)
        self.assertIsNotNone(user_1)
        self.assertIsNotNone(user_2)
        self.assertIsNotNone(node_1)
        self.assertIsNotNone(node_2)
        self.client.login(username='user1', password='password')

        request = self.client.post(reverse('user_profile:like_profile'), {'slug': user_2.id})
        self.assertEqual(request.status_code, 200)
        self.assertIsNotNone(LikeProfile.objects.get(to_profile=user_2.profile, from_profile=user_1.profile))
        self.assertTrue(node_1.like.is_connected(node_2))


    def test_like_profile_bad_slug(self):
        user_1 = User.objects.get(username='user1')
        user_2 = User.objects.get(username='user2')
        node_1 = NodeProfile.nodes.get(user_id=user_1.id)
        node_2 = NodeProfile.nodes.get(user_id=user_2.id)
        self.assertIsNotNone(user_1)
        self.assertIsNotNone(user_2)
        self.assertIsNotNone(node_1)
        self.assertIsNotNone(node_2)
        self.client.login(username='user1', password='password')

        request = self.client.post(reverse('user_profile:like_profile'), {'slug': 'fooX€'})
        self.assertEqual(request.status_code, 404)
        self.assertEqual(LikeProfile.objects.filter(to_profile=user_2.profile, from_profile=user_1.profile).count(), 0)
        self.assertFalse(node_1.like.is_connected(node_2))

    def test_like_profile_without_slug(self):
        user_1 = User.objects.get(username='user1')
        user_2 = User.objects.get(username='user2')
        node_1 = NodeProfile.nodes.get(user_id=user_1.id)
        node_2 = NodeProfile.nodes.get(user_id=user_2.id)
        self.assertIsNotNone(user_1)
        self.assertIsNotNone(user_2)
        self.assertIsNotNone(node_1)
        self.assertIsNotNone(node_2)
        self.client.login(username='user1', password='password')

        request = self.client.post(reverse('user_profile:like_profile'), {})
        self.assertEqual(request.status_code, 404)
        self.assertEqual(LikeProfile.objects.filter(to_profile=user_2.profile, from_profile=user_1.profile).count(), 0)
        self.assertFalse(node_1.like.is_connected(node_2))

    def test_remove_like_profile(self):
        user_1 = User.objects.get(username='user1')
        user_2 = User.objects.get(username='user2')
        node_1 = NodeProfile.nodes.get(user_id=user_1.id)
        node_2 = NodeProfile.nodes.get(user_id=user_2.id)
        self.assertIsNotNone(user_1)
        self.assertIsNotNone(user_2)
        self.assertIsNotNone(node_1)
        self.assertIsNotNone(node_2)
        self.client.login(username='user1', password='password')

        request = self.client.post(reverse('user_profile:like_profile'), {'slug': user_2.id})
        self.assertEqual(request.status_code, 200)

        request = self.client.post(reverse('user_profile:like_profile'), {'slug': user_2.id})
        self.assertEqual(request.status_code, 200)

        self.assertEqual(LikeProfile.objects.filter(to_profile=user_2.profile, from_profile=user_1.profile).count(), 0)
        self.assertFalse(node_1.like.is_connected(node_2))


    @classmethod
    def tearDownClass(cls):
        clear_neo4j_database(db)
