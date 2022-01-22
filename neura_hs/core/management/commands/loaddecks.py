from django.core.management.base import BaseCommand
import json

from core.services.decks import DumpDeckListSerializer


class Command(BaseCommand):
    help = 'Loads deck data from JSON file'

    def add_arguments(self, parser):
        parser.add_argument('tempfile', nargs='?', default=None, help='Use temporary dump file')

    def handle(self, *args, **options):
        temp = options['tempfile']
        path = temp if temp else 'core/management/commands/decks.json'
        data = load_deck_data(path)
        serializer = DumpDeckListSerializer(data=data, many=True)
        if serializer.is_valid():
            serializer.save()
        else:
            self.stdout.write(f'Invalid JSON dump\n{serializer.errors}')


def load_deck_data(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data
