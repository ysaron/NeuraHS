from django.core.management.base import BaseCommand
from core.services.update import ImageUpdater


class Command(BaseCommand):
    help = 'Downloads rendered cards and card thumbnails from art.hearthstonejson.com'

    def add_arguments(self, parser):
        parser.add_argument('-u', '--update', nargs='+', required=False, help='Space separated card IDs')

    def handle(self, *args, **options):
        id_list = options.get('update')

        upd = ImageUpdater(id_list)
        upd.update()

        if fail_list := upd.report['FAIL_DOWNLOAD']:
            self.stdout.write(f'!!! Failed to download:\n{fail_list}')
