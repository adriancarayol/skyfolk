from django.test import TestCase
from neomodel import db, clear_neo4j_database
from ..models import RelationShipProfile
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from ..node_models import NodeProfile


class FollowUserTest(TestCase):
    def setUp(self):
        clear_neo4j_database(db)
        User.objects.create_user(username='user1', password='password')
        User.objects.create_user(username='user2', password='password')

    def test_follow_user(self):
        user_1 = User.objects.get(username='user1')
        user_2 = User.objects.get(username='user2')
        node_1 = NodeProfile.nodes.get(user_id=user_1.id)
        node_2 = NodeProfile.nodes.get(user_id=user_2.id)

        self.assertIsNotNone(user_1)
        self.assertIsNotNone(user_2)
        self.assertIsNotNone(node_1)
        self.assertIsNotNone(node_2)
        self.assertIsNotNone(user_1.profile)
        self.assertIsNotNone(user_2.profile)

        self.client.login(username='user1', password='password')
        request = self.client.post(reverse('user_profile:request_friend'), {'slug': user_2.id})
        self.assertEqual(request.status_code, 200)
        relationship = RelationShipProfile.objects.get(to_profile=user_2.profile, from_profile=user_1.profile)
        self.assertIsNotNone(relationship)
        self.assertEqual(relationship.to_profile, user_2.profile)
        self.assertEqual(relationship.from_profile, user_1.profile)
        self.assertTrue(node_1.follow.is_connected(node_2))

    def test_follow_user_without_slug(self):
        user_1 = User.objects.get(username='user1')
        user_2 = User.objects.get(username='user2')
        node_1 = NodeProfile.nodes.get(user_id=user_1.id)
        node_2 = NodeProfile.nodes.get(user_id=user_2.id)

        self.assertIsNotNone(user_1)
        self.assertIsNotNone(user_2)
        self.assertIsNotNone(node_1)
        self.assertIsNotNone(node_2)
        self.assertIsNotNone(user_1.profile)
        self.assertIsNotNone(user_2.profile)

        self.client.login(username='user1', password='password')
        request = self.client.post(reverse('user_profile:request_friend'))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(RelationShipProfile.objects.filter(to_profile=user_2.profile,
                                                            from_profile=user_1.profile).count(), 0)
        self.assertFalse(node_1.follow.is_connected(node_2))

    def test_follow_user_with_wrong_slug(self):
        user_1 = User.objects.get(username='user1')
        user_2 = User.objects.get(username='user2')
        node_1 = NodeProfile.nodes.get(user_id=user_1.id)
        node_2 = NodeProfile.nodes.get(user_id=user_2.id)

        self.assertIsNotNone(user_1)
        self.assertIsNotNone(user_2)
        self.assertIsNotNone(node_1)
        self.assertIsNotNone(node_2)
        self.assertIsNotNone(user_1.profile)
        self.assertIsNotNone(user_2.profile)

        self.client.login(username='user1', password='password')
        self.assertRaises(ValueError, self.client.post, path=reverse('user_profile:request_friend'),
                          data={'slug': '1123fasf'})
        self.assertEqual(RelationShipProfile.objects.filter(to_profile=user_2.profile,
                                                            from_profile=user_1.profile).count(), 0)
        self.assertFalse(node_1.follow.is_connected(node_2))

    def test_remove_follow_user(self):
        self.test_follow_user()
        user_1 = User.objects.get(username='user1')
        user_2 = User.objects.get(username='user2')
        node_1 = NodeProfile.nodes.get(user_id=user_1.id)
        node_2 = NodeProfile.nodes.get(user_id=user_2.id)
        request = self.client.post(reverse('user_profile:remove_relationship'), {'slug': user_2.id})
        self.assertEqual(request.status_code, 200)
        self.assertEqual(RelationShipProfile.objects.filter(to_profile=user_2.profile,
                                                            from_profile=user_1.profile).count(), 0)
        self.assertFalse(node_1.follow.is_connected(node_2))

    def test_remove_follow_user_without_slug(self):
        self.test_follow_user()
        user_1 = User.objects.get(username='user1')
        user_2 = User.objects.get(username='user2')
        node_1 = NodeProfile.nodes.get(user_id=user_1.id)
        node_2 = NodeProfile.nodes.get(user_id=user_2.id)
        request = self.client.post(reverse('user_profile:remove_relationship'))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(RelationShipProfile.objects.filter(to_profile=user_2.profile,
                                                            from_profile=user_1.profile).count(), 1)
        self.assertTrue(node_1.follow.is_connected(node_2))

    def test_remove_follow_user_wrong_slug(self):
        self.test_follow_user()
        user_1 = User.objects.get(username='user1')
        user_2 = User.objects.get(username='user2')
        node_1 = NodeProfile.nodes.get(user_id=user_1.id)
        node_2 = NodeProfile.nodes.get(user_id=user_2.id)
        self.assertRaises(ValueError, self.client.post, path=reverse('user_profile:remove_relationship'),
                          data={'slug': '1123fasf'})
        self.assertEqual(RelationShipProfile.objects.filter(to_profile=user_2.profile,
                                                            from_profile=user_1.profile).count(), 1)
        self.assertTrue(node_1.follow.is_connected(node_2))

    @classmethod
    def tearDownClass(cls):
        clear_neo4j_database(db)
