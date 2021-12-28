import pytest
from django.urls import reverse_lazy
from decks.models import Deck
from gallery.models import RealCard, FanCard


class TestDeckViews:
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


class TestFanCardViews:
    @pytest.mark.django_db
    def test_fancard_list_view(self, client):
        response = client.get(reverse_lazy('gallery:fancards'))
        assert response.status_code == 200, 'Список фан-карт недоступен'

    @pytest.mark.django_db
    def test_fancard_instance_view(self, fan_card, user_client):
        user, auth_client = user_client
        card = fan_card('Approved Fan Card', user.author, approved=True)
        response = auth_client.get(reverse_lazy('gallery:fan_card', kwargs={'card_slug': card.slug}))
        assert response.status_code == 200, 'Прошедшая премодерацию фан-карта недоступна'

    @pytest.mark.django_db
    def test_not_approved_fancard_instance_view(self, fan_card, user_client):
        user, auth_client = user_client
        card = fan_card('Not approved card', user.author)
        response = auth_client.get(reverse_lazy('gallery:fan_card', kwargs={'card_slug': card.slug}))
        assert response.status_code == 404, 'Доступна не прошедшая премодерацию фан-карта'

    @pytest.mark.django_db
    def test_fancard_create_view(self, user_client):
        user, auth_client = user_client
        response = auth_client.get(reverse_lazy('gallery:createcard'))
        assert response.status_code == 200, 'Страница создания карты недоступна для авторизованного пользователя'

    @pytest.mark.django_db
    def test_fancard_create_unauthorized_view(self, client):
        response = client.get(reverse_lazy('gallery:createcard'))
        assert response.status_code == 302, 'Страница создания карты доступна для неавторизованного пользователя'

    @pytest.mark.django_db
    def test_fancard_update_unauthorized(self, client, user_client, fan_card):
        auth_user, auth_client = user_client
        card = fan_card('Approved card', auth_user.author, approved=True)
        client.logout()
        response = client.get(reverse_lazy('gallery:updatecard', kwargs={'card_slug': card.slug}))
        assert response.status_code == 302, 'Карта доступна для редактирования неавторизованным пользователем'

    @pytest.mark.django_db
    def test_fancard_update_wrong_author(self, user_client, admin_user, fan_card):
        auth_user, auth_client = user_client
        card = fan_card('Approved card', admin_user.author, approved=True)
        response = auth_client.get(reverse_lazy('gallery:updatecard', kwargs={'card_slug': card.slug}))
        assert response.status_code == 403, 'Карта автора доступна для редактирования другим пользователем'

    @pytest.mark.django_db
    def test_fancard_update_by_its_author(self, user_client, fan_card):
        auth_user, auth_client = user_client
        card = fan_card('Approved card', auth_user.author, approved=True)
        response = auth_client.get(reverse_lazy('gallery:updatecard', kwargs={'card_slug': card.slug}))
        assert response.status_code == 200, 'Карта автора недоступна для редактирования'

    @pytest.mark.django_db
    def test_fancard_delete_unauthorized(self, client, user_client, fan_card):
        auth_user, auth_client = user_client
        card = fan_card('Approved card', auth_user.author, approved=True)
        client.logout()
        response = client.get(reverse_lazy('gallery:deletecard', kwargs={'card_slug': card.slug}))
        assert response.status_code == 302, 'Карта доступна для удаления неавторизованным пользователем'

    @pytest.mark.django_db
    def test_fancard_delete_wrong_author(self, user_client, admin_user, fan_card):
        auth_user, auth_client = user_client
        card = fan_card('Approved card', admin_user.author, approved=True)
        response = auth_client.get(reverse_lazy('gallery:deletecard', kwargs={'card_slug': card.slug}))
        assert response.status_code == 403, 'Карта автора доступна для удаления другим пользователем'

    @pytest.mark.django_db
    def test_fancard_delete_by_its_author(self, user_client, fan_card):
        auth_user, auth_client = user_client
        card = fan_card('Approved card', auth_user.author, approved=True)
        response = auth_client.get(reverse_lazy('gallery:deletecard', kwargs={'card_slug': card.slug}))
        assert response.status_code == 200, 'Карта автора недоступна для удаления'


class TestAuthorViews:
    @pytest.mark.django_db
    def test_author_list_view(self, client):
        response = client.get(reverse_lazy('gallery:authors'))
        assert response.status_code == 200, 'Список авторов карт недоступен'


class TestRealCardViews:
    @pytest.mark.django_db
    def test_real_card_list_view(self, client):
        response = client.get(reverse_lazy('gallery:realcards'))
        assert response.status_code == 200, 'Список карт Hearthstone недоступен'

    @pytest.mark.django_db
    def test_real_card_instance_view(self, client, real_card):
        card = real_card('New Hearthstone Card', card_id='NEW_TEST01', dbf_id=999999)
        response = client.get(reverse_lazy('gallery:real_card', kwargs={'card_slug': card.slug}))
        assert response.status_code == 200, 'Карта Hearthstone недоступна для просмотра'
