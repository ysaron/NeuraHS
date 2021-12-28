import pytest
from django.urls import reverse_lazy
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


class TestDBUpdateCommand:
    @pytest.mark.django_db
    def test_write_card_classes(self, hs_db_worker):
        hs_db_worker.write_card_classes()
        card_classes = CardClass.objects.all()
        assert card_classes.count() == 4
        assert card_classes.filter(name='Shaman').exists(), 'Класс не был записан в БД'
        assert card_classes.filter(name_ru='Шаман').exists(), 'Класс не был переведен'

    @pytest.mark.django_db
    def test_write_tribes(self, hs_db_worker):
        hs_db_worker.write_tribes()
        tribes = Tribe.objects.all()
        assert tribes.count() == 2
        assert tribes.filter(name='Demon').exists(), 'Раса не была записана в БД'
        assert tribes.filter(name_ru='Демон').exists(), 'Раса не была переведена'

    @pytest.mark.django_db
    def test_write_card_sets(self, hs_db_worker):
        hs_db_worker.write_card_sets()
        card_sets = CardSet.objects.all()
        assert card_sets.count() == 3
        assert card_sets.filter(name='Mean Streets of Gadgetzan').exists(), 'Набор не был записан в БД'
        assert card_sets.filter(name_ru='Злачный город Прибамбасск').exists(), 'Набор не был переведен'
        assert card_sets.filter(name='unknown').exists(), 'Набор по умолчанию не был записан в БД'

    @pytest.mark.django_db
    def test_write_cards(self, hs_db_worker):
        hs_db_worker.write_card_classes()
        hs_db_worker.write_tribes()
        hs_db_worker.write_card_sets()
        hs_db_worker.write_en_cards(rewrite=False)
        hs_db_worker.add_ru_translation()
        cards = RealCard.objects.all()
        assert cards.count() == 2
        assert cards.filter(name='Aya Blackpaw').exists(), 'Карта не была записана в БД'
        assert cards.filter(name_ru='Айя Черная Лапа').exists(), 'Карта не была переведена'


