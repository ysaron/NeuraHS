from django.core.management.base import BaseCommand
import json

from core.services.decks import DumpDeckListSerializer
from decks.models import Deck


class Command(BaseCommand):
    help = 'Dumps deck data to JSON file'

    def handle(self, *args, **options):
        with open('core/management/commands/decks.json', 'w', encoding='utf-8') as f:
            json.dump(get_deck_data(), f, indent=2)


def get_deck_data():
    """ Возвращает сериализованные данные всех колод в БД, необходимые и достаточные для их восстановления """

    decks = Deck.objects.all()
    response = DumpDeckListSerializer(decks, many=True)
    return response.data
