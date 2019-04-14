from rest_framework.test import APITestCase
from rest_framework import status


class UserProfileAPITest(APITestCase):
    def test_create_account(self):
        """
        Ensure we can create a new account object.
        """
        url = "/api/users/"
        self.client.login(username="adrian", password="1518")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
