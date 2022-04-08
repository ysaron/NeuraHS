import requests
import os
from pathlib import Path
from io import BytesIO
from PIL import Image
from django.conf import settings
from django.core.files import File


SUPPORTED_LANGUAGES = {'en': 'enUS', 'ru': 'ruRU'}


class Picture:

    def __init__(self, language: str = 'en'):
        self.language = language
        self.__check_language()
        self.name = ''
        self.path = Path()
        self.url = 'https://art.hearthstonejson.com/v1'
        self.data = BytesIO()

    def __check_language(self):
        languages_list = SUPPORTED_LANGUAGES.keys()
        if self.language not in languages_list:
            raise ValueError(f'Unsupported language: {self.language}. Allowed: {", ".join(languages_list)}')

    def download(self):
        """ Скачивает файл по URL в файлоподобный объект self.data """
        r = requests.get(self.url, stream=True)
        if r.status_code != 200:
            raise ConnectionError(f'Cannot download [{self.url}]\nError code: {r.status_code}')

        for chunk in r.iter_content(1024):
            self.data.write(chunk)

    @property
    def exists(self):
        """ Проверяет наличие изображения в файловой системе """
        return self.path.is_file()

    def erase(self):
        """ Удаляет изображение из файловой системы """
        self.path.unlink(missing_ok=True)

    @property
    def for_imagefield(self):
        """ Возвращает словарь с именованными аргументами для ImageField (для распаковки **) """
        return {'name': os.path.basename(self.path), 'content': File(self.data)}

    def __str__(self):
        return f'{self.path} [{self.language}]'


class CardRender(Picture):
    def __init__(self, name: str, language: str = 'en'):
        super().__init__(language=language)
        self.name = name
        self.path: Path = settings.MEDIA_ROOT / 'cards' / self.language / f'{self.name}.png'
        self.url = f'{self.url}/render/latest/{SUPPORTED_LANGUAGES[self.language]}/256x/{self.name}.png'


class Thumbnail(Picture):
    def __init__(self, name: str):
        super().__init__()
        self.name = name
        self.path: Path = settings.MEDIA_ROOT / 'cards' / 'thumbnails' / f'{self.name}.png'
        self.url = f'{self.url}/tiles/{self.name}.png'

    def fade(self, from_perc: int = 20, to_perc: int = 50):
        """
        Добавляет изображению затухание справа налево
        :param from_perc: % от ширины изображения (отсчет слева направо), определяющий место начала затухания
        :param to_perc: % от ширины изображения (отсчет слева направо), определяющий место конца затухания
        """
        if not all(0 <= x <= 100 for x in (from_perc, to_perc)):
            raise ValueError('from_perc and to_perc must be in range 0-100')

        with Image.open(self.path) as orig:
            orig.putalpha(255)  # добавление альфа-канала без прозрачности
            width, height = orig.size
            pixels = orig.load()  # получение r/w доступа к изображению на уровне пикселей

            from_, to_ = from_perc / 100, to_perc / 100

            for x in range(int(width * from_), int(width * to_)):
                alpha = int((x - width * from_) * 255 / width / (to_ - from_))
                for y in range(height):
                    pixels[x, y] = pixels[x, y][:3] + (alpha,)
            for x in range(0, int(width * from_)):
                for y in range(height):
                    pixels[x, y] = pixels[x, y][:3] + (0,)

            orig.save(self.path)


class DeckRender(Picture):
    pass
