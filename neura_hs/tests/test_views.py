import pytest
from django.urls import reverse_lazy
from decks.models import Deck


class TestDecks:
    @pytest.mark.django_db
    def test_create_deck_view(self, client):
        response = client.get(reverse_lazy('decks:index'))
        assert response.status_code == 200, 'Страница создания колоды недоступна'

    @pytest.mark.django_db
    def test_all_decks_view(self, client):
        response = client.get(reverse_lazy('decks:all_decks'))
        assert response.status_code == 200, 'Список всех колод недоступен'

    @pytest.mark.django_db
    def test_user_decks_superuser_view(self, admin_client):
        response = admin_client.get(reverse_lazy('decks:user_decks'))
        assert response.status_code == 200, 'Личное хранилище колод суперюзера недоступно'

    @pytest.mark.django_db
    def test_user_decks_unauthorized_view(self, client):
        response = client.get(reverse_lazy('decks:user_decks'))
        assert response.status_code == 302, 'Личное хранилище колод не должно быть доступно без авторизации!'

    @pytest.mark.django_db
    def test_public_deck_instance_view(self, client, deck, deckstring2):
        deck = Deck.create_from_deckstring(deckstring2)
        response = client.get(reverse_lazy('decks:deck-detail', kwargs={'deck_id': deck.pk}))
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_save_deck(self, user_client, deck, deckstring2):
        user, client = user_client
        data = {'string_to_save': deckstring2, 'deck_name': 'Some Rogue deck'}
        response = client.post(reverse_lazy('decks:index'), data)
        assert Deck.named.count() == 1
        deck_obj = Deck.named.first()
        assert deck_obj.name == 'Some Rogue deck', 'Колода сохранена с неверным названием'
        assert deck_obj.author == user.author, 'Автор колоды не совпал с никнеймом сохранившего ее пользователя'
        assert response.status_code == 302, 'После сохранения колоды должно происходить перенаправление на ее страницу'

    @pytest.mark.django_db
    def test_get_random_deckstring_ajax_view(self, client):
        response = client.get(reverse_lazy('decks:get_random_deckstring'))
        assert response.status_code == 302, 'Должно быть доступно только для AJAX-запросов'


class TestCards:
    pass
