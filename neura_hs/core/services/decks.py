from django.db.models import Q, Count

from decks.models import Deck


def find_similar_decks(target_deck: Deck):
    """ Возвращает список колод того же формата и класса с большим числом совпадений карт """

    if not target_deck:
        return

    # первичная фильтрация (без учета кол-ва вхождений карт в колоду) на уровне БД
    similar_raw = Deck.nameless.filter(
        deck_format=target_deck.deck_format,
        deck_class=target_deck.deck_class,
    ).exclude(
        string=target_deck.string
    ).annotate(
        num_matches=Count('pk', filter=Q(cards__in=target_deck.cards.all()))
    ).filter(
        num_matches__gt=9
    ).order_by('-num_matches')

    # строгая фильтрация
    similar_decks = []
    for deck in similar_raw:
        num_strict_matches = 0
        for card in deck.included_cards:
            if card in target_deck.included_cards:
                if card.number == 2 and target_deck.included_cards.get(pk=card.pk).number == 2:
                    num_strict_matches += 2
                else:
                    num_strict_matches += 1
        if num_strict_matches >= 20:
            similar_decks.append(deck)
        else:
            # queryset similar_raw отсортирован по числу совпадений карт,
            # поэтому в нем больше не встретятся колоды, удовлетворяющие условию
            break

    return similar_decks
