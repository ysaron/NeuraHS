from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend

from .serializers import (
    RealCardListSerializer,
    RealCardDetailSerializer,
    DeckSerializer,
)
from .services.filters import RealCardFilter, DeckFilter
from core.services.utils import get_clean_deckstring
from core.exceptions import DecodeError, UnsupportedCards
from gallery.models import RealCard, CardClass, CardSet, Tribe
from decks.models import Deck, Format, Inclusion


class RealCardListAPIView(generics.ListAPIView):
    """ Вывод списка карт Hearthstone """

    queryset = RealCard.objects.all()
    serializer_class = RealCardListSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RealCardFilter


class RealCardDetailAPIView(generics.RetrieveAPIView):
    """ Вывод карты Hearthstone """

    queryset = RealCard.objects.all()
    serializer_class = RealCardDetailSerializer
    lookup_field = 'dbf_id'


class DeckListAPIView(generics.ListAPIView):
    """ Вывод списка колод """

    queryset = Deck.nameless.all()
    serializer_class = DeckSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = DeckFilter


class DeckDetailAPIView(generics.RetrieveAPIView):
    """ Вывод колоды """
    queryset = Deck.nameless.all()
    serializer_class = DeckSerializer


class ViewDeckAPIView(APIView):
    """ Расшифровка колоды из кода """

    def post(self, request):
        if deckstring := request.data.get('d'):
            try:
                deckstring = get_clean_deckstring(deckstring)
                deck = Deck.create_from_deckstring(deckstring)
                serializer = DeckSerializer(deck)
                return Response(serializer.data)
            except DecodeError as de:
                return Response({'error': str(de)})
            except UnsupportedCards as u:
                return Response({'error': str(u)})

        return Response()
