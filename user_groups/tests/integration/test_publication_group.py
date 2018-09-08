import pytest
from publications.views import publication_new_view
from publications_groups.models import PublicationGroup
from django.urls import reverse
from django.core.management import call_command


"""
  Integration test for create new publications in groups
"""


@pytest.fixture(scope='function')
def prepare_user(client, django_user_model, monkeypatch):
    username = "user1"
    password = "bar"
    username2 = "user2"

    django_user_model.objects.create_user(username=username, password=password)
    django_user_model.objects.create_user(username=username2, password=password)
    client.login(username=username, password=password)
    client.login(username=username2, password=password)
    call_command('badgify_sync', 'badges')
