from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
import requests
import os
from io import BytesIO
from tqdm import tqdm
from time import sleep

from gallery.models import RealCard


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


def get_image(url: str) -> BytesIO:
    """ Скачивает файл по URL в файлоподобный объект io.BytesIO """

    r = requests.get(url, stream=True)
    if r.status_code != 200:
        raise ConnectionError(f'Could not download {url}\nError code: {r.status_code}')

    sleep(0.3)

    file = BytesIO()
    for chunk in r.iter_content(1024):
        file.write(chunk)
    return file


def download_missing_images():
    """ Скачивает отсутствующие рендеры и миниатюры карт, связывает их с соотв. ImageField """

    cards = RealCard.includibles.all()
    for card in tqdm(cards, desc='Download missing images', ncols=120):

        image_en_path = settings.MEDIA_ROOT / 'cards' / 'en' / f'{card.card_id}.png'
        if not image_en_path.is_file():
            image_en = get_image(f'https://art.hearthstonejson.com/v1/render/latest/enUS/256x/{card.card_id}.png')
            card.image_en.save(os.path.basename(image_en_path), File(image_en))

        image_ru_path = settings.MEDIA_ROOT / 'cards' / 'ru' / f'{card.card_id}.png'
        if not image_ru_path.is_file():
            image_ru = get_image(f'https://art.hearthstonejson.com/v1/render/latest/ruRU/256x/{card.card_id}.png')
            card.image_ru.save(os.path.basename(image_ru_path), File(image_ru))

        thumbnail_path = settings.MEDIA_ROOT / 'cards' / 'thumbnails' / f'{card.card_id}.png'
        if not thumbnail_path.is_file():
            thumbnail = get_image(f'https://art.hearthstonejson.com/v1/tiles/{card.card_id}.png')
            card.thumbnail.save(os.path.basename(thumbnail_path), File(thumbnail))

        card.save()


def update_specific_images(card_ids: list):
    """ Обновляет рендеры конкретных карт """

    cards = RealCard.includibles.filter(card_id__in=card_ids)
    if cards.count() < len(card_ids):
        tqdm.write(f'Warning! Not all cards were found. Perhaps there is an error in the passed card_ids.')
    for card in tqdm(cards, desc='Update specific images', ncols=120):

        image_en_path = settings.MEDIA_ROOT / 'cards' / 'en' / f'{card.card_id}.png'
        try:
            image_en_path.unlink()
        except OSError:
            tqdm.write(f'There is no image_en to delete for {card.card_id} ({card.name})')
        image_en = get_image(f'https://art.hearthstonejson.com/v1/render/latest/enUS/256x/{card.card_id}.png')
        card.image_en.save(os.path.basename(image_en_path), File(image_en))

        image_ru_path = settings.MEDIA_ROOT / 'cards' / 'ru' / f'{card.card_id}.png'
        try:
            image_ru_path.unlink()
        except OSError:
            tqdm.write(f'There is no image_en to delete for {card.card_id} ({card.name})')
        image_ru = get_image(f'https://art.hearthstonejson.com/v1/render/latest/ruRU/256x/{card.card_id}.png')
        card.image_ru.save(os.path.basename(image_ru_path), File(image_ru))

        card.save()
