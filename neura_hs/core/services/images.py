import requests
import os
import time
from pathlib import Path
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

from django.conf import settings
from django.core.files import File

from decks.models import Deck
from gallery.models import RealCard


SUPPORTED_LANGUAGES = {
    'en': {'loc': 'enUS', 'field': 'image_en'},
    'ru': {'loc': 'ruRU', 'field': 'image_ru'}}

IMAGE_CLASS_MAP = {
    'Demon Hunter': {'stripe': 'demonhunter_stripe.png'},
    'Warrior': {'stripe': 'warrior_stripe.png'},
    'Warlock': {'stripe': 'warlock_stripe.png'},
    'Shaman': {'stripe': 'shaman_stripe.png'},
    'Rogue': {'stripe': 'rogue_stripe.png'},
    'Priest': {'stripe': 'priest_stripe.png'},
    'Paladin': {'stripe': 'paladin_stripe.png'},
    'Mage': {'stripe': 'mage_stripe.png'},
    'Hunter': {'stripe': 'hunter_stripe.png'},
    'Druid': {'stripe': 'druid_stripe.png'},
}


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
        self.url = f'{self.url}/render/latest/{SUPPORTED_LANGUAGES[self.language]["loc"]}/256x/{self.name}.png'


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
    def __init__(self, name: str, deck: Deck, language: str):
        super().__init__(language=language)
        self.name = name
        self.deck = deck
        self.path = self.__generate_path()
        self.width = 2380
        self.height = 1644
        self.coord: list[tuple[int, int]] = []

        self.__pre_format_render()
        self.__render = Image.new('RGBA', size=self.size, color='#333')
        self.__draw = ImageDraw.Draw(self.__render)

    @property
    def size(self) -> tuple[int, int]:
        return self.width, self.height

    def __generate_path(self) -> Path:
        filename = f'{self.deck.pk}{int(time.time()):x}.png'
        return settings.MEDIA_ROOT / 'decks' / filename

    def create(self):
        """ Создает рендер """

        self.__draw_cards()
        self.__draw_header()
        self.__draw_footer()
        self.__render.save(self.data, 'PNG')

    def __pre_format_render(self):
        """ Устанавливает разрешение и координаты плейсхолдеров в зависимости от кол-ва карт """
        cards = self.deck.included_cards
        amount = cards.count()
        vertical_num = 3
        horizontal_num = (amount + vertical_num - 1) // vertical_num    # деление с округлением вверх
        self.width = 238 * horizontal_num + 10

        x, y = 0, 100
        for card in cards:
            if x >= self.width - 238:
                x = 0
                y += 360

            # исходные PNG карт-героев смещены --> корректировка
            coords = (x - 8, y - 18) if card.card_type == RealCard.CardTypes.HERO else (x, y)
            self.coord.append(coords)
            x += 238

    def __draw_cards(self):
        """ Добавляет на рендер колоды рендеры ее карт """
        image_field = SUPPORTED_LANGUAGES[self.language]['field']
        for card, c in zip(self.deck.included_cards, self.coord):
            with Image.open(getattr(card, image_field), 'r') as card_render:
                if card.number > 1:
                    cr2 = card_render.rotate(angle=-5, center=(350, 150), resample=Image.BICUBIC, expand=True)
                    cr2 = self.__adjust_brightness(cr2, factor=0.8)
                    self.__render.paste(cr2, c, mask=cr2)
                card_render = self.__adjust_brightness(card_render, factor=1.2)
                card_render = self.__contrast(card_render, 1.2)
                self.__render.paste(card_render, c, mask=card_render)

    def __draw_header(self):
        """ Добавляет на рендер шапку с заголовком """
        self.__draw_title_stripe()
        self.__draw_title_text()

    def __draw_title_stripe(self):
        """ Добавляет на рендер полосу-рамку для заголовка """
        with Image.open(settings.MEDIA_ROOT / 'decks' / 'title.png', 'r') as title:
            w, h = title.size
            self.__render.paste(title, ((self.width - w) // 2, 10))

    def __draw_title_text(self):
        """ Добавляет на рендер текст заголовка """
        path: Path = settings.BASE_DIR / 'core' / 'services' / 'fonts' / 'consola.ttf'
        font = ImageFont.truetype(str(path), 44, encoding='utf-8')
        title_text = self.name
        w, h = self.__draw.textsize(title_text, font=font)
        self.__draw.text(
            ((self.width - w) // 2, 40),
            title_text,
            fill='white',
            font=font,
            stroke_width=2,
            stroke_fill='black',
        )

    def __draw_footer(self):
        """ Добавляет на рендер нижний колонтитул """
        stripe_png = IMAGE_CLASS_MAP[self.deck.deck_class.service_name]['stripe']
        with Image.open(settings.MEDIA_ROOT / 'decks' / stripe_png, 'r') as stripe:
            w, h = stripe.size
            self.__render.paste(stripe, ((self.width - w) // 2, 1230))

        self.__draw_craft_cost()

    def __draw_mana_curve(self):
        """  """
        pass

    def __draw_craft_cost(self):
        """ Добавляет на нижний колонтитул информацию о стоимости колоды """
        with Image.open(settings.MEDIA_ROOT / 'decks' / 'craft_cost.png', 'r') as craft_cost:
            w, h = craft_cost.size
            self.__render.paste(craft_cost, ((self.width - w) // 2, 1384), mask=craft_cost)

        path: Path = settings.BASE_DIR / 'core' / 'services' / 'fonts' / 'consola.ttf'
        font = ImageFont.truetype(str(path), 48, encoding='utf-8')
        craft_cost_text = str(self.deck.get_craft_cost().get('basic'))
        w, h = self.__draw.textsize(craft_cost_text, font=font)
        self.__draw.text(
            ((self.width - w + 90) // 2, 1432 - h // 2),
            craft_cost_text,
            fill='#ffffff',
            font=font,
            stroke_width=1,
            stroke_fill='black',
        )

    @staticmethod
    def __adjust_brightness(image: Image, factor: float) -> Image:
        """
        :param image: изображение
        :param factor: 1 - без эффекта, меньше - затемнение, больше - осветление
        """
        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(factor)

    @staticmethod
    def __contrast(image: Image, factor: float = 1):
        """
        Возвращает копию изображения с измененным контрастом
        :param image: изображение
        :param factor: 1 - без эффекта, меньше - уменьшить контраст, больше - увеличить
        """
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(factor)
