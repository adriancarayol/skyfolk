from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from neomodel import db


class ProfileInterests(APIView):
    """
    List interests of user profile
    """
    authentication_classes = (authentication.SessionAuthentication, 
        authentication.BasicAuthentication)
    permission_classes = (permissions.IsAdminUser,)

    def get(self, request, username):
        my_interests, _ = db.cypher_query(
            "MATCH (n:NodeProfile)-[:INTEREST]-(interest:TagProfile) WHERE n.title='%s' RETURN interest.title SKIP 10 LIMIT 3000" % username)
        interests = [item for sublist in my_interests for item in sublist]
        return Response(interests)