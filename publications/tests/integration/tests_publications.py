import pytest
from publications.views import publication_new_view
from publications.models import Publication
from django.urls import reverse
from django.core.management import call_command

"""
  Integration test for create new publications
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


def test_create_new_publication(rf, django_user_model, prepare_user):
    user = django_user_model.objects.get(username='user1')

    data = {
        'board_owner': user.id,
        'content': 'foo'
    }

    request = rf.post(reverse('publications:new_publication'), data)
    request.user = user
    response = publication_new_view(request)

    try:
        created = Publication.objects.get(board_owner=user.id, author=user.id)
    except Publication.DoesNotExist:
        created = None

    assert response is not None
    assert created is not None
    assert response.status_code == 302


def test_create_new_publication_other_user(rf, django_user_model, prepare_user):
    user = django_user_model.objects.get(username='user1')
    user2 = django_user_model.objects.get(username='user2')

    data = {
        'board_owner': user.id,
        'content': 'foo'
    }

    request = rf.post(reverse('publications:new_publication'), data)
    request.user = user2
    response = publication_new_view(request)

    try:
        created = Publication.objects.get(board_owner=user.id, author=user.id)
    except Publication.DoesNotExist:
        created = None

    assert response is not None
    assert created is None
    assert response.status_code == 200


def test_create_new_reply_other_user(rf, django_user_model, prepare_user):
    user = django_user_model.objects.get(username='user1')
    user2 = django_user_model.objects.get(username='user2')

    data = {
        'board_owner': user.id,
        'content': 'foo'
    }

    request = rf.post(reverse('publications:new_publication'), data)
    request.user = user
    response = publication_new_view(request)

    assert response is not None
    assert response.status_code == 302

    try:
        created = Publication.objects.get(board_owner=user.id, author=user.id)
    except Publication.DoesNotExist:
        created = None

    assert created is not None

    data['parent'] = created.id
    request2 = rf.post(reverse('publications:new_publication'), data)
    request2.user = user2
    response2 = publication_new_view(request)

    try:
        created2 = Publication.objects.get(board_owner=user.id, author=user2.id)
    except Publication.DoesNotExist:
        created2 = None

    assert response2 is not None
    assert response2.status_code == 302
    assert created2 is None

