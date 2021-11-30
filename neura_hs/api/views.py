from rest_framework import generics

from .serializers import (
    RealCardListSerializer,
    RealCardDetailSerializer,
    DeckSerializer,
    UserDeckSerializer
)
from gallery.models import RealCard, CardClass, CardSet, Tribe
from decks.models import Deck, Format, Inclusion


class RealCardListAPIView(generics.ListAPIView):
    """ Вывод списка карт Hearthstone """

    queryset = RealCard.objects.all()
    serializer_class = RealCardListSerializer


class RealCardDetailAPIView(generics.RetrieveAPIView):
    """ Вывод карты Hearthstone """

    queryset = RealCard.objects.all()
    serializer_class = RealCardDetailSerializer
    lookup_field = 'dbf_id'


class DeckListAPIView(generics.ListAPIView):
    """ Вывод списка колод """

    queryset = Deck.nameless.all()
    serializer_class = DeckSerializer


class UserDeckListAPIView(generics.ListAPIView):
    """ Вывод списка сохраненных колод текущего пользователя """

    serializer_class = UserDeckSerializer

    def get_queryset(self):
        decks = Deck.named.filter(author=self.request.user.author)
        return decks


class DeckDetailAPIView(generics.RetrieveAPIView):
    """ Вывод колоды """
    queryset = Deck.nameless.all()
    serializer_class = DeckSerializer
