from neomodel import db, clear_neo4j_database
from django.test import TestCase
from django.contrib.auth.models import User
from user_profile.models import NodeProfile
from django.db import transaction

class UserTestClass(TestCase):
    def setUp(self):
        clear_neo4j_database(db)

    def test_create_object(self):
        try:
            with transaction.atomic(using="default"):
                with db.transaction:
                    sql_row = User.objects.create(username="example", password="foo")
                    neo4j_node = NodeProfile(title="example", user_id=sql_row.id).save()
                    raise Exception
        except Exception as e:
            pass

        neo4j_q = NodeProfile.nodes.get_or_none(title="example")
        sql_q = User.objects.filter(username="example").first()

        self.assertIsNone(neo4j_q)
        self.assertIsNone(sql_q)

    def test_create_node(self):
        try:
            with transaction.atomic(using="default"):
                with db.transaction:
                    sql_row = User.objects.create(username="example", password="foo")
                    neo4j_node = NodeProfile(title="example", user_id=sql_row.id).save()
        except Exception as e:
            sql_row = None
            neo4j_node = None

        self.assertIsNotNone(sql_row)
        self.assertIsNotNone(neo4j_node)
        self.assertEqual(sql_row.id, neo4j_node.user_id)
