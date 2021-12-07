from rest_framework import generics, viewsets
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
from gallery.models import RealCard
from decks.models import Deck


class RealCardViewSet(viewsets.ReadOnlyModelViewSet):
    """ Getting Hearthstone cards """
    queryset = RealCard.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RealCardFilter
    lookup_field = 'dbf_id'

    def get_serializer_class(self):
        if self.action == 'list':
            return RealCardListSerializer
        elif self.action == 'retrieve':
            return RealCardDetailSerializer


class DeckListAPIView(generics.ListAPIView):
    """ Getting a list of decks """

    queryset = Deck.nameless.all()
    serializer_class = DeckSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = DeckFilter


class DeckDetailAPIView(generics.RetrieveAPIView):
    """ Getting a specific deck """
    queryset = Deck.nameless.all()
    serializer_class = DeckSerializer


class ViewDeckAPIView(APIView):
    """ Decoding the deck from code """

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
