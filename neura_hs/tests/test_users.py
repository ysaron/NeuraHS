import pytest
from rest_framework import status
from django.contrib.auth.models import User
from gallery.models import Author


@pytest.mark.django_db
def test_user_author_create(user):
    """ Проверка, создается ли новый пользователь со связанным объектом автора """
    assert User.objects.count() == 1
    assert Author.objects.count() == 1
    assert Author.objects.get(user=user)


@pytest.mark.django_db
def test_unauthorized_access(client, limited_access_url):
    response = client.get(limited_access_url)
    assert response.status_code == status.HTTP_302_FOUND


@pytest.mark.django_db
def test_authorized_access(admin_client, user_client, limited_access_url):
    user, client = user_client
    response_admin = admin_client.get(limited_access_url)
    response_user = client.get(limited_access_url)
    assert response_admin.status_code == status.HTTP_200_OK
    assert response_user.status_code == status.HTTP_200_OK
