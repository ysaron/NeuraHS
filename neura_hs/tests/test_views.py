import pytest
from django.urls import reverse_lazy
from rest_framework import status


class TestDeckViews:
    @pytest.mark.django_db
    def test_create_deck_view(self, client):
        response = client.get(reverse_lazy('decks:index'))
        assert response.status_code == status.HTTP_200_OK, 'Страница создания колоды недоступна'

    @pytest.mark.django_db
    def test_all_decks_view(self, client):
        response = client.get(reverse_lazy('decks:all_decks'))
        assert response.status_code == status.HTTP_200_OK, 'Список всех колод недоступен'

    @pytest.mark.django_db
    def test_user_decks_superuser_view(self, admin_client):
        response = admin_client.get(reverse_lazy('decks:user_decks'))
        assert response.status_code == status.HTTP_200_OK, 'Личное хранилище колод суперюзера недоступно'

    @pytest.mark.django_db
    def test_user_decks_unauthorized_view(self, client):
        response = client.get(reverse_lazy('decks:user_decks'))
        assert response.status_code == status.HTTP_302_FOUND, 'Личное хранилище колод доступно без авторизации'

    @pytest.mark.django_db
    def test_get_random_deckstring_ajax_view(self, client):
        response = client.get(reverse_lazy('decks:get_random_deckstring'))
        assert response.status_code == status.HTTP_302_FOUND, 'Должно быть доступно только для AJAX-запросов'


class TestFanCardViews:
    @pytest.mark.django_db
    def test_fancard_list_view(self, client):
        response = client.get(reverse_lazy('gallery:fancards'))
        assert response.status_code == status.HTTP_200_OK, 'Список фан-карт недоступен'

    @pytest.mark.django_db
    def test_fancard_instance_view(self, fan_card, user_client):
        user, auth_client = user_client
        card = fan_card('Approved Fan Card', user.author, approved=True)
        response = auth_client.get(reverse_lazy('gallery:fan_card', kwargs={'card_slug': card.slug}))
        assert response.status_code == status.HTTP_200_OK, 'Прошедшая премодерацию фан-карта недоступна'

    @pytest.mark.django_db
    def test_not_approved_fancard_instance_view(self, fan_card, user_client):
        user, auth_client = user_client
        card = fan_card('Not approved card', user.author)
        response = auth_client.get(reverse_lazy('gallery:fan_card', kwargs={'card_slug': card.slug}))
        assert response.status_code == status.HTTP_404_NOT_FOUND, 'Доступна не прошедшая премодерацию фан-карта'

    @pytest.mark.django_db
    def test_fancard_create_view(self, user_client):
        user, auth_client = user_client
        response = auth_client.get(reverse_lazy('gallery:createcard'))
        assert response.status_code == status.HTTP_200_OK, 'Страница создания карты недоступна для авторизованного ' \
                                                           'пользователя'

    @pytest.mark.django_db
    def test_fancard_create_unauthorized_view(self, client):
        response = client.get(reverse_lazy('gallery:createcard'))
        assert response.status_code == status.HTTP_302_FOUND, 'Страница создания карты доступна для ' \
                                                              'неавторизованного пользователя'

    @pytest.mark.django_db
    def test_fancard_update_unauthorized(self, client, user_client, fan_card):
        auth_user, auth_client = user_client
        card = fan_card('Approved card', auth_user.author, approved=True)
        client.logout()
        response = client.get(reverse_lazy('gallery:updatecard', kwargs={'card_slug': card.slug}))
        assert response.status_code == status.HTTP_302_FOUND, 'Карта доступна для редактирования неавторизованным ' \
                                                              'пользователем'

    @pytest.mark.django_db
    def test_fancard_update_wrong_author(self, user_client, admin_user, fan_card):
        auth_user, auth_client = user_client
        card = fan_card('Approved card', admin_user.author, approved=True)
        response = auth_client.get(reverse_lazy('gallery:updatecard', kwargs={'card_slug': card.slug}))
        assert response.status_code == status.HTTP_403_FORBIDDEN, 'Карта автора доступна для редактирования другим ' \
                                                                  'пользователем'

    @pytest.mark.django_db
    def test_fancard_update_by_its_author(self, user_client, fan_card):
        auth_user, auth_client = user_client
        card = fan_card('Approved card', auth_user.author, approved=True)
        response = auth_client.get(reverse_lazy('gallery:updatecard', kwargs={'card_slug': card.slug}))
        assert response.status_code == status.HTTP_200_OK, 'Карта автора недоступна для редактирования'

    @pytest.mark.django_db
    def test_fancard_delete_unauthorized(self, client, user_client, fan_card):
        auth_user, auth_client = user_client
        card = fan_card('Approved card', auth_user.author, approved=True)
        client.logout()
        response = client.get(reverse_lazy('gallery:deletecard', kwargs={'card_slug': card.slug}))
        assert response.status_code == status.HTTP_302_FOUND, 'Карта доступна для удаления неавторизованным ' \
                                                              'пользователем'

    @pytest.mark.django_db
    def test_fancard_delete_wrong_author(self, user_client, admin_user, fan_card):
        auth_user, auth_client = user_client
        card = fan_card('Approved card', admin_user.author, approved=True)
        response = auth_client.get(reverse_lazy('gallery:deletecard', kwargs={'card_slug': card.slug}))
        assert response.status_code == status.HTTP_403_FORBIDDEN, 'Карта автора доступна для удаления другим ' \
                                                                  'пользователем'

    @pytest.mark.django_db
    def test_fancard_delete_by_its_author(self, user_client, fan_card):
        auth_user, auth_client = user_client
        card = fan_card('Approved card', auth_user.author, approved=True)
        response = auth_client.get(reverse_lazy('gallery:deletecard', kwargs={'card_slug': card.slug}))
        assert response.status_code == status.HTTP_200_OK, 'Карта автора недоступна для удаления'


class TestAuthorViews:
    @pytest.mark.django_db
    def test_author_list_view(self, client):
        response = client.get(reverse_lazy('gallery:authors'))
        assert response.status_code == status.HTTP_200_OK, 'Список авторов карт недоступен'


class TestRealCardViews:
    @pytest.mark.django_db
    def test_real_card_list_view(self, client):
        response = client.get(reverse_lazy('gallery:realcards'))
        assert response.status_code == status.HTTP_200_OK, 'Список карт Hearthstone недоступен'

    @pytest.mark.django_db
    def test_real_card_instance_view(self, client, real_card):
        card = real_card('New Hearthstone Card', card_id='NEW_TEST01', dbf_id=999999)
        response = client.get(reverse_lazy('gallery:real_card', kwargs={'card_slug': card.slug}))
        assert response.status_code == status.HTTP_200_OK, 'Карта Hearthstone недоступна для просмотра'
