import pytest
from django.urls import reverse_lazy


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(username='TestUser01', email='test@test.testtest', password='12344321')


@pytest.fixture
def user_client(user, client):
    client.force_login(user)
    return user, client


@pytest.fixture
def limited_access_url():
    return reverse_lazy('gallery:createcard')
