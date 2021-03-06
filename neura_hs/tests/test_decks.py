from django.core.management import call_command
import pytest
from core.services.deck_codes import parse_deckstring
from core.exceptions import DecodeError


@pytest.mark.django_db
def test_parse_deckstring(deckstring, deck_data):
    with pytest.raises(DecodeError):
        parse_deckstring('some random string')
    result = parse_deckstring(deckstring)
    assert isinstance(result, tuple), f'parse_deckstring возвращает {type(result)} вместо tuple'
    assert len(result) == 3, 'данные о колоде должны быть кортежем из 3 элементов'
    cards, heroes, format_ = result
    assert isinstance(cards, list), 'cards должно быть списком'
    for card in cards:
        assert isinstance(card, tuple), 'данные о карте должны быть кортежем'
        assert len(card) == 2, 'кортеж карты должен содержать 2 элемента: dbf_id и кол-во вхождений в колоду'
        assert all(isinstance(i, int) for i in card), 'элементы кортежа карты должны иметь тип int'
        assert card[1] in [1, 2], 'кол-во вхождений карты в колоду должно быть равно 1 или 2'
    assert set(cards) == set(deck_data[0]), 'данные о картах не совпадают'
    assert heroes == deck_data[1], 'данные о герое не совпадают'
    assert format_ == deck_data[2], 'данные о формате не совпадают'
