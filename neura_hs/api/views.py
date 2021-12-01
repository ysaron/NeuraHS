from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend

from .serializers import (
    RealCardListSerializer,
    RealCardDetailSerializer,
    DeckSerializer,
    UserDeckSerializer
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


# class ViewDeckAPIView(APIView):
#     """  """
#
#     def get(self, request):
#         if deckstring := request.GET.get('d'):
#             try:
#                 deckstring = get_clean_deckstring(deckstring)
#                 print(deckstring)
#                 deckstring = deckstring.replace(' ', '+')
#                 print(deckstring)
#                 deck = Deck.create_from_deckstring(deckstring)
#                 serializer = DeckSerializer(deck)
#                 return Response(serializer.data)
#             except DecodeError as de:
#                 raise de
#             except UnsupportedCards as u:
#                 raise u
#
#         return Response()
#
#     def post(self, request):
#         print(request.POST)
#         if deckstring := request.POST.get('d'):
#             try:
#                 deckstring = get_clean_deckstring(deckstring)
#                 print(deckstring)
#                 deckstring = deckstring.replace(' ', '+')
#                 print(deckstring)
#                 deck = Deck.create_from_deckstring(deckstring)
#                 serializer = DeckSerializer(deck)
#                 return Response(serializer.data)
#             except DecodeError as de:
#                 raise de
#             except UnsupportedCards as u:
#                 raise u
#
#         return Response()

