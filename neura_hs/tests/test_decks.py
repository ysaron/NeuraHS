import pytest
from decks.models import Deck, Format


# @pytest.mark.django_db
# def test_create_deck_from_deckstring():
#     # rogue-108
#     Deck.create_from_deckstring('AAEBAaIHBq8QmxSRvAKA0wL+mgOs6wMMm8gC5dEC6vMC+5oDragDqssDiNADpNED99QDkp8E7qAE+6UEAA==')
#     assert Deck.nameless.count() == 1


@pytest.mark.django_db
def test_write_formats(hs_db_worker):
    hs_db_worker.write_formats()
    formats = Format.objects.all()
    assert formats.count() == 4
    assert formats.filter(name='Wild').exists(), 'Формат не был записан в БД'
    assert formats.filter(name_ru='Вольный').exists(), 'Формат не был переведен'

