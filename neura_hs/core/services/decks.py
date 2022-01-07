from django.db.models import Q, Count

from decks.models import Deck


def find_similar_decks(target_deck: Deck):
    """ Возвращает колоды того же формата и класса с большим числом совпадений карт (>= 20) """

    if not target_deck:
        return

    return Deck.nameless.filter(
        deck_format=target_deck.deck_format,
        deck_class=target_deck.deck_class,
    ).exclude(
        string=target_deck.string
    ).annotate(
        num_matches=2 * Count(
            'cards',
            filter=Q(inclusions__number=2) & Q(cards__in=target_deck.cards.filter(inclusions__number=2))
        ) + Count(
            'cards',
            filter=Q(inclusions__number=2) & Q(cards__in=target_deck.cards.filter(inclusions__number=1))
        ) + Count(
            'cards',
            filter=Q(inclusions__number=1) & Q(cards__in=target_deck.cards.all())
        ),
    ).filter(
        num_matches__gt=19
    ).order_by('-num_matches')
