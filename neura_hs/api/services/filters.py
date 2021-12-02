from django_filters import rest_framework as filters

from gallery.models import RealCard, CardClass, CardSet
from decks.models import Deck, Format


class CharInFilter(filters.BaseInFilter, filters.CharFilter):
    """
    BaseInFilter - валидация разделенных запятыми входящих значений
    CharFilter - фильтрация по тексту (по умолчанию фильтрация по id)
    """
    pass


class RealCardFilter(filters.FilterSet):
    """  """
    card_id = filters.CharFilter()
    dbf_id = filters.NumberFilter()
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    classes = CharInFilter(field_name='card_class__name', lookup_expr='in')
    ctype = filters.ChoiceFilter(field_name='card_type', choices=RealCard.CardTypes.choices)
    cset = filters.ModelChoiceFilter(queryset=CardSet.objects.all(), field_name='card_set', to_field_name='name')
    rarity = filters.ChoiceFilter(choices=RealCard.Rarities.choices)
    cost = filters.RangeFilter()
    attack = filters.RangeFilter()
    health = filters.RangeFilter()
    armor = filters.RangeFilter()
    durability = filters.RangeFilter()

    class Meta:
        model = RealCard
        fields = ('card_id', 'dbf_id', 'name', 'classes', 'ctype', 'cset', 'rarity', 'cost', 'attack', 'health',
                  'durability', 'armor')


class DeckFilter(filters.FilterSet):
    """  """
    dclass = filters.ModelChoiceFilter(queryset=CardClass.objects.filter(collectible=True),
                                       field_name='deck_class', to_field_name='name')
    dformat = filters.ModelChoiceFilter(queryset=Format.objects.all(),
                                        field_name='deck_format', to_field_name='name')
    date = filters.DateTimeFromToRangeFilter(field_name='created')
    cards = filters.CharFilter(field_name='cards', method='filter_decks_by_cards')

    class Meta:
        model = Deck
        fields = ('dformat', 'dclass', 'date', 'cards')

    def filter_decks_by_cards(self, queryset, name, value):
        """ Позволяет фильтровать колоды по картам, указывая их dbf_id через запятую """

        for dbf_id in value.split(","):
            queryset = queryset.filter(cards__dbf_id=dbf_id)

        return queryset
