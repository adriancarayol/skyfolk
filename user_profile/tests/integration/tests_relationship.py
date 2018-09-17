from user_profile.views import remove_relationship
from django.test import TestCase
from neomodel import db, clear_neo4j_database
from user_profile.models import RelationShipProfile, LikeProfile
from django.contrib.auth.models import User
from django.urls import reverse
from user_profile.node_models import NodeProfile
from unittest import mock
from django.test.client import RequestFactory


class FollowUserTest(TestCase):
    def setUp(self):
        clear_neo4j_database(db)
        User.objects.create_user(username='user1', password='password')
        User.objects.create_user(username='user2', password='password')

    def test_follow_user(self):
        user_1 = User.objects.get(username='user1')
        user_2 = User.objects.get(username='user2')
        node_1 = NodeProfile.nodes.get(title=user_1.username)
        node_2 = NodeProfile.nodes.get(title=user_2.username)

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
        node_1 = NodeProfile.nodes.get(title=user_1.username)
        node_2 = NodeProfile.nodes.get(title=user_2.username)

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
        node_1 = NodeProfile.nodes.get(title=user_1.username)
        node_2 = NodeProfile.nodes.get(title=user_2.username)

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
        node_1 = NodeProfile.nodes.get(title=user_1.username)
        node_2 = NodeProfile.nodes.get(title=user_2.username)
        request = self.client.post(reverse('user_profile:remove_relationship'), {'slug': user_2.id})
        self.assertEqual(request.status_code, 200)
        self.assertEqual(RelationShipProfile.objects.filter(to_profile=user_2.profile,
                                                            from_profile=user_1.profile).count(), 0)
        self.assertFalse(node_1.follow.is_connected(node_2))

    def test_remove_follow_user_without_slug(self):
        self.test_follow_user()
        user_1 = User.objects.get(username='user1')
        user_2 = User.objects.get(username='user2')
        node_1 = NodeProfile.nodes.get(title=user_1.username)
        node_2 = NodeProfile.nodes.get(title=user_2.username)
        request = self.client.post(reverse('user_profile:remove_relationship'))
        self.assertEqual(request.status_code, 200)
        self.assertEqual(RelationShipProfile.objects.filter(to_profile=user_2.profile,
                                                            from_profile=user_1.profile).count(), 1)
        self.assertTrue(node_1.follow.is_connected(node_2))

    def test_remove_follow_user_wrong_slug(self):
        self.test_follow_user()
        user_1 = User.objects.get(username='user1')
        user_2 = User.objects.get(username='user2')
        node_1 = NodeProfile.nodes.get(title=user_1.username)
        node_2 = NodeProfile.nodes.get(title=user_2.username)
        self.assertRaises(ValueError, self.client.post, path=reverse('user_profile:remove_relationship'),
                          data={'slug': '1123fasf'})
        self.assertEqual(RelationShipProfile.objects.filter(to_profile=user_2.profile,
                                                            from_profile=user_1.profile).count(), 1)
        self.assertTrue(node_1.follow.is_connected(node_2))

    def test_remove_follow_user_exception(self):
        self.test_follow_user()
        user_1 = User.objects.get(username='user1')
        user_2 = User.objects.get(username='user2')
        node_1 = NodeProfile.nodes.get(title=user_1.username)
        node_2 = NodeProfile.nodes.get(title=user_2.username)

        with mock.patch.object(RelationShipProfile.objects, 'filter') as mock_method:
            mock_method.side_effect = Exception("test error")
            r = RequestFactory().post(reverse('user_profile:remove_relationship'), {'slug': user_2.id})
            r.user = user_1
            remove_relationship(r)
            self.assertTrue(node_1.follow.is_connected(node_2))

        self.assertEqual(RelationShipProfile.objects.filter(to_profile=user_2.profile,
                                                            from_profile=user_1.profile).count(), 1)
    def test_block_user(self):
        user_1 = User.objects.get(username='user1')
        user_2 = User.objects.get(username='user2')
        node_1 = NodeProfile.nodes.get(title=user_1.username)
        node_2 = NodeProfile.nodes.get(title=user_2.username)
        self.assertIsNotNone(user_1)
        self.assertIsNotNone(user_2)
        self.assertIsNotNone(node_1)
        self.assertIsNotNone(node_2)

        self.client.login(username='user1', password='password')
        request = self.client.post(reverse('user_profile:bloq_user'), {'id_user': user_2.id})
        self.assertEqual(request.status_code, 200)

        self.assertEqual(RelationShipProfile.objects.filter(to_profile=user_2.profile,
                                                            from_profile=user_1.profile, type=3).count(), 1)
        self.assertTrue(node_1.bloq.is_connected(node_2))


    def test_block_follow(self):
        self.test_follow_user()
        user_1 = User.objects.get(username='user1')
        user_2 = User.objects.get(username='user2')
        node_1 = NodeProfile.nodes.get(title=user_1.username)
        node_2 = NodeProfile.nodes.get(title=user_2.username)

        request = self.client.post(reverse('user_profile:bloq_user'), {'id_user': user_2.id})
        self.assertEqual(request.status_code, 200)

        self.assertEqual(RelationShipProfile.objects.filter(to_profile=user_2.profile,
                                                            from_profile=user_1.profile, type=3).count(), 1)
        self.assertTrue(node_1.bloq.is_connected(node_2))


    def test_block_user_liked(self):
        user_1 = User.objects.get(username='user1')
        user_2 = User.objects.get(username='user2')
        node_1 = NodeProfile.nodes.get(title=user_1.username)
        node_2 = NodeProfile.nodes.get(title=user_2.username)
        self.assertIsNotNone(user_1)
        self.assertIsNotNone(user_2)
        self.assertIsNotNone(node_1)
        self.assertIsNotNone(node_2)
        self.client.login(username='user1', password='password')

        request = self.client.post(reverse('user_profile:like_profile'), {'slug': user_2.id})
        self.assertEqual(request.status_code, 200)
        self.assertIsNotNone(LikeProfile.objects.get(to_profile=user_2.profile, from_profile=user_1.profile))

        request = self.client.post(reverse('user_profile:bloq_user'), {'id_user': user_2.id})
        self.assertEqual(request.status_code, 200)

        self.assertEqual(RelationShipProfile.objects.filter(to_profile=user_2.profile,
                                                            from_profile=user_1.profile, type=3).count(), 1)
        self.assertEqual(LikeProfile.objects.filter(to_profile=user_2.profile, from_profile=user_1.profile).count(), 0)
        self.assertTrue(node_1.bloq.is_connected(node_2))


    @classmethod
    def tearDownClass(cls):
        clear_neo4j_database(db)
