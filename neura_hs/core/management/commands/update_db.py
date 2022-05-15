from django.core.management.base import BaseCommand
import time

from core.services.update import Updater


class Command(BaseCommand):
    help = 'Update the card database'

    def add_arguments(self, parser):
        parser.add_argument('-r', '--rewrite', action='store_true', help='Rewrite all cards')

    def handle(self, *args, **options):
        start = time.perf_counter()
        upd = Updater(self.stdout.write, rewrite=options['rewrite'])
        upd.update()
        end = time.perf_counter()
        self.stdout.write(f'Database update took {end - start:.2f}s')
        self.stdout.write('Renders need to be updated:')
        self.stdout.write(' '.join(upd.to_be_updated))
