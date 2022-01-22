from django.db.models import Q, Count
from rest_framework import serializers

from decks.models import Deck, Format, Inclusion
from gallery.models import RealCard
from .deck_codes import parse_deckstring


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


class DumpDeckListSerializer(serializers.ModelSerializer):

    created = serializers.DateTimeField()

    class Meta:
        model = Deck
        fields = ('id', 'string', 'created', 'name', 'author')

    def create(self, validated_data) -> None:
        string, author, created = validated_data['string'], validated_data['author'], validated_data['created']
        if Deck.objects.filter(string=string, author=author, created=created).exists():
            return
        deck = Deck()
        deck.name = validated_data['name']
        deck.author = author
        deck.string = string
        deck.created = created

        cards, heroes, format_ = parse_deckstring(deck.string)
        deck.deck_class = RealCard.objects.get(dbf_id=heroes[0]).card_class.all().first()
        deck.deck_format = Format.objects.get(numerical_designation=format_)
        deck.save()

        for dbf_id, number in cards:
            card = RealCard.includibles.get(dbf_id=dbf_id)
            ci = Inclusion(deck=deck, card=card, number=number)
            ci.save()
            deck.cards.add(card)
