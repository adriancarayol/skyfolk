import pytest
from user_profile.views import InterestsView

"""
  Integration test for introducing profile interest
"""


@pytest.fixture(scope='function')
def prepare_user(client, django_user_model):
    username = "user1"
    password = "bar"
    django_user_model.objects.create_user(username=username, password=password)
    client.login(username=username, password=password)


def test_introduce_interest(rf, django_user_model, prepare_user):
    tags = ('tag', 'TaG', 'TAG')

    data = {
        'tags[]': tags,
        'choice[]': ()
    }

    request = rf.post('/config/interests/', data)
    request.user = django_user_model.objects.get(username='user1')
    response = InterestsView.as_view()(request)

    user_node = NodeProfile.nodes.get(title='user1')
    tags = TagProfile.nodes.filter(title__iexact='tag')

    assert user_node is not None
    assert tags is not None
    assert len(tags) == 1
    assert response.status_code == 200
    assert response is not None
