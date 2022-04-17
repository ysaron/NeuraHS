from django.core.management.base import BaseCommand
import json

from core.services.deck_utils import DumpDeckListSerializer
from decks.models import Deck


class Command(BaseCommand):
    help = 'Dumps deck data to JSON file'

    def add_arguments(self, parser):
        parser.add_argument('tempfile', nargs='?', default=None, help='Use temporary dump file for tests')

    def handle(self, *args, **options):
        temp = options['tempfile']
        path = temp if temp else 'core/management/commands/decks.json'
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(get_deck_data(), f, indent=2)


def get_deck_data():
    """ Возвращает сериализованные данные всех колод в БД, необходимые и достаточные для их восстановления """

    decks = Deck.objects.all()
    response = DumpDeckListSerializer(decks, many=True)
    return response.data
