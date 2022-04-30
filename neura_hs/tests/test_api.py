import pytest
from rest_framework import status


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
