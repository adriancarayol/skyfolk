from neomodel import db, clear_neo4j_database
from django.test import TestCase
from user_profile.models import TagProfile, NodeProfile

class YourTestClass(TestCase):
    def setUp(self):
        clear_neo4j_database(db)

    def test_connect_user_to_tag(self):
        adrian = NodeProfile.get_or_create({"title": "adrian"})[0]
        tag = TagProfile.get_or_create({"title": "YOKSETIO"})[0]
        tag.user.connect(adrian)
        print(adrian)
        assert adrian != None
