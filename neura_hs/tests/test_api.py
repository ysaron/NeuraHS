import pytest
from rest_framework import status
from decks.models import Deck


class TestCardsAPI:
    @pytest.mark.django_db
    def test_get_card_list_api(self, api_client, real_card):
        real_card('Some test card', 'TEST01', 123456)
        real_card('Another test card', 'TEST02', 135790)
        real_card('Test Test Test', 'TEST03', 99999999)

        params = {'cost_min': '6', 'cost_max': '8',
                  'attack_min': '9', 'attack_max': '9',
                  'health_min': '5', 'health_max': '7',
                  'rarity': 'E',
                  'ctype': 'M',
                  'classes': 'Rogue,Mage,Druid,Hunter'}
        response = api_client.get('/api/v1/cards/', data=params)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3
        assert all(card['card_class'][0] == 'Rogue' for card in response.data)
        assert any(card['dbf_id'] == 123456 for card in response.data)

    @pytest.mark.django_db
    def test_get_single_card_api(self, api_client, real_card):
        real_card('Yet another card', 'TEST001', 19283746)
        response = api_client.get('/api/v1/cards/19283746/')
        assert response.status_code == status.HTTP_200_OK


class TestDecksAPI:
    @pytest.mark.django_db
    def test_get_deck_list_api(self, api_client, deck, deckstring2):
        Deck.create_from_deckstring(deckstring2)
        params = {'dformat': 'Wild',
                  'dclass': 'Rogue',
                  'cards': '59556,43392,47594'}
        response = api_client.get('/api/v1/decks/', data=params)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert len(response.data[0]['cards']) == 18
        assert sum(card['number'] for card in response.data[0]['cards']) == 30

    @pytest.mark.django_db
    def test_get_single_deck_api(self, api_client, deck, deckstring2):
        deck = Deck.create_from_deckstring(deckstring2)
        response = api_client.get(f'/api/v1/decks/{deck.pk}/')
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.django_db
    def test_decode_deck_api(self, api_client, deck, deckstring2):
        params = {'d': deckstring2}
        response = api_client.post('/api/v1/decode_deck/', data=params)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['cards']) == 18
        assert sum(card['number'] for card in response.data['cards']) == 30
