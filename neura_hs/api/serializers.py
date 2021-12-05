from rest_framework import serializers

from gallery.models import RealCard, CardClass, CardSet, Tribe
from decks.models import Deck, Format, Inclusion


class FilterCardListSerializer(serializers.ListSerializer):

    def to_representation(self, data):
        data = data.filter(collectible=True)
        return super().to_representation(data)

    def update(self, instance, validated_data):
        pass


class RealCardSerializer(serializers.ModelSerializer):
    """  """
    card_type = serializers.CharField(source='get_card_type_display')
    card_set = serializers.SlugRelatedField(slug_field='name', read_only=True)
    card_class = serializers.SlugRelatedField(slug_field='name', read_only=True, many=True)
    rarity = serializers.CharField(source='get_rarity_display')
    tribe = serializers.SlugRelatedField(slug_field='name', read_only=True, many=True)
    spell_school = serializers.CharField(source='get_spell_school_display')


class RealCardListSerializer(RealCardSerializer):
    """  """

    class Meta:
        list_serializer_class = FilterCardListSerializer
        model = RealCard
        fields = ('dbf_id', 'card_id', 'name', 'collectible', 'card_type', 'cost', 'attack', 'health', 'durability',
                  'armor', 'card_class', 'card_set', 'text', 'rarity')
        ref_name = 'CardList'


class RealCardDetailSerializer(RealCardSerializer):
    """  """

    class Meta:
        model = RealCard
        fields = ('dbf_id', 'card_id', 'name', 'collectible', 'battlegrounds', 'card_type', 'cost', 'attack', 'health',
                  'durability', 'armor', 'card_class', 'card_set', 'text', 'flavor', 'rarity', 'tribe', 'spell_school')
        ref_name = 'Card'


class RealCardInDeckSerializer(RealCardSerializer):
    """  """

    class Meta:
        model = RealCard
        fields = ('dbf_id', 'card_id', 'name', 'card_type', 'cost', 'attack', 'health', 'durability', 'armor',
                  'card_class', 'card_set', 'text', 'flavor', 'rarity', 'tribe', 'spell_school')
        ref_name = 'CardInDeck'


class InclusionSerializer(serializers.ModelSerializer):
    """ Сериализация списка карт в колоде """

    card = RealCardInDeckSerializer()

    class Meta:
        model = Inclusion
        fields = ('card', 'number')
        ref_name = 'CardInclusion'


class DeckSerializer(serializers.ModelSerializer):

    deck_class = serializers.SlugRelatedField(slug_field='name', read_only=True)
    deck_format = serializers.SlugRelatedField(slug_field='name', read_only=True)
    cards = InclusionSerializer(source='inclusions', many=True)
    created = serializers.DateTimeField(format='%d.%m.%Y')

    class Meta:
        model = Deck
        fields = ('id', 'deck_format', 'deck_class', 'string', 'created', 'cards')
