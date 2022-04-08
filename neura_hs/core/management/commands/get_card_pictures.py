from django.core.management.base import BaseCommand
from tqdm import tqdm
from time import sleep
from gallery.models import RealCard
from core.services.images import CardRender, Thumbnail


class Command(BaseCommand):
    help = 'Downloads rendered cards and card thumbnails from art.hearthstonejson.com'

    def add_arguments(self, parser):
        parser.add_argument('-u', '--update', nargs='+', required=False, help='Space separated card IDs')

    def handle(self, *args, **options):
        id_list = options.get('update')

        if id_list:
            update_specific_images(id_list)
        else:
            download_missing_images()

        if fail_list := report['FAIL_DOWNLOAD']:
            self.stdout.write(f'!!! Failed to download:\n{fail_list}')


report = {
    'FAIL_DOWNLOAD': [],
    'FAIL_PROCESS': [],
}


def update_specific_images(card_ids: list):
    """ Обновляет рендеры конкретных карт """

    cards = RealCard.includibles.filter(card_id__in=card_ids)
    if cards.count() < len(card_ids):
        tqdm.write(f'Warning! Not all cards were found. Perhaps there is an error in the passed card_ids.')

    for card in tqdm(cards, desc='Update specific images', ncols=120):
        image_en = CardRender(name=card.card_id, language='en')
        image_ru = CardRender(name=card.card_id, language='ru')

        for image, image_field in zip((image_en, image_ru), (card.image_en, card.image_ru)):
            try:
                image.download()
                sleep(0.3)
                image.erase()
                image_field.save(**image.for_imagefield)
            except ConnectionError:
                report['FAIL_DOWNLOAD'].append(card)

        card.save()


def download_missing_images():
    """ Скачивает отсутствующие рендеры и миниатюры карт, связывает их с соотв. ImageField """

    cards = RealCard.includibles.all()
    for card in tqdm(cards, desc='Download missing images', ncols=120):
        image_en = CardRender(name=card.card_id, language='en')
        image_ru = CardRender(name=card.card_id, language='ru')
        thumbnail = Thumbnail(name=card.card_id)

        for image, image_field in zip(
                (image_en, image_ru, thumbnail),
                (card.image_en, card.image_ru, card.thumbnail)
        ):
            if not image.exists:
                try:
                    image.download()
                    sleep(0.3)
                    image_field.save(**image.for_imagefield)
                except ConnectionError:
                    report['FAIL_DOWNLOAD'].append(card)

        if thumbnail.exists:
            thumbnail.fade()
        card.save()
