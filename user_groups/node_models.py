from django_neomodel import DjangoNode
from neomodel import StringProperty, IntegerProperty, RelationshipFrom, RelationshipTo


class NodeGroup(DjangoNode):
    title = StringProperty(unique_index=True)
    group_id = IntegerProperty(unique_index=True)
    members = RelationshipFrom('user_profile.node_models.NodeProfile', 'MEMBER')
    interest = RelationshipTo('user_profile.node_models.TagProfile', 'INTEREST_GROUP')
    likes = RelationshipFrom('user_profile.node_models.NodeProfile', 'LIKE_GROUP')

    class Meta:
        app_label = 'group_node'