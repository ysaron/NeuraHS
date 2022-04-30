import pytest
from gallery.models import RealCard, FanCard, CardClass, Tribe, CardSet


class TestCardCreation:
    @pytest.mark.django_db
    def test_realcard_create(self, real_card):
        real_card('New Test Minion', 'TEST01_TEST', 9999999)
        assert RealCard.objects.count() == 1
        assert RealCard.objects.filter(name='New Test Minion',
                                       card_set__name='Scholomance Academy',
                                       card_class__name='Rogue',
                                       tribe__name='Beast').exists()

    @pytest.mark.django_db
    def test_fancard_create(self, fan_card, user_client):
        user, auth_client = user_client
        fan_card('New Fan Card', user.author)
        assert FanCard.objects.count() == 1
        assert FanCard.objects.filter(name='New Fan Card',
                                      card_class__name='Mage',
                                      author=user.author).exists()
