from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.conf import settings
from django.db import transaction
import json
import jmespath
import requests
import re
from tqdm import tqdm
import time

from core.services.deck_codes import parse_deckstring
from gallery.models import RealCard, CardClass, Tribe, CardSet, Mechanic
from decks.models import Deck, Format, Inclusion

LOCALE_LIST = ['enUS', 'ruRU']
ENDPOINT_LIST = ['info', 'cards']

C_TYPES = {
    'minion': RealCard.CardTypes.MINION,
    'spell': RealCard.CardTypes.SPELL,
    'weapon': RealCard.CardTypes.WEAPON,
    'hero': RealCard.CardTypes.HERO,
    'hero power': RealCard.CardTypes.HEROPOWER,
}
RARITIES = {
    'free': RealCard.Rarities.NO_RARITY,
    'common': RealCard.Rarities.COMMON,
    'rare': RealCard.Rarities.RARE,
    'epic': RealCard.Rarities.EPIC,
    'legendary': RealCard.Rarities.LEGENDARY,
}
SPELL_SCHOOLS = {
    'holy': RealCard.SpellSchools.HOLY,
    'shadow': RealCard.SpellSchools.SHADOW,
    'nature': RealCard.SpellSchools.NATURE,
    'fel': RealCard.SpellSchools.FEL,
    'fire': RealCard.SpellSchools.FIRE,
    'frost': RealCard.SpellSchools.FROST,
    'arcane': RealCard.SpellSchools.ARCANE,
}


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


class HsApiConnection:

    def __init__(self, endpoint: str, locale: str = 'enUS'):
        self.__headers = {'x-rapidapi-key': settings.X_RAPIDARI_KEY, 'x-rapidapi-host': settings.HSAPI_HOST}
        self.__endpoint = endpoint
        self.__locale = locale
        self.__check_endpoint()
        self.__check_locale()

    def __check_endpoint(self) -> None:
        if self.__endpoint not in ENDPOINT_LIST:
            raise ValueError(f'Endpoint must be one of {ENDPOINT_LIST}')

    def __check_locale(self) -> None:
        if self.__locale not in LOCALE_LIST:
            raise ValueError(f'Locale must be one of {LOCALE_LIST}')

    def get(self):
        """ Выполняет запрос, возвращает данные в JSON """
        url = settings.HSAPI_BASEURL + self.__endpoint.lower()
        r = requests.get(url=url, headers=self.__headers, params={'locale': self.__locale}, stream=True)
        r.raise_for_status()
        return r.json()


class Updater:

    def __init__(self, writer, rewrite: bool = False):
        self.__rewrite = rewrite
        self.__writer = writer
        self.__en_cards = None
        self.__ru_cards = None
        self.__card_classes = None
        self.__tribes = None
        self.__card_sets = None
        self.__mechanics = None
        self.__hidden_mechanics = ['AIMustPlay', 'AffectedBySpellPower', 'ImmuneToSpellpower', 'InvisibleDeathrattle',
                                   'OneTurnEffect']
        self.__additional_mechanics = ['Lackey', 'Dormant', 'Choose One', 'Start of Game', 'Immune']
        self.__info = None
        self.to_be_updated: list[str] = []

        self.__get_cards()
        self.__get_auxiliary_entities()

    def __get_cards(self):
        """ Формирует данные карт для записи в БД """
        endpoint = 'cards'
        en_connection = HsApiConnection(endpoint, locale='enUS')
        self.__writer('Cards (EN): API request...')
        en_cards_raw = en_connection.get()
        self.__writer('Cards (EN): data cleaning...')
        self.__en_cards = jmespath.search(expression="*[?type!='Enchantment'][]", data=en_cards_raw)

        self.__card_sets = list(set(jmespath.search(expression="*[?type!='Enchantment'][].cardSet", data=en_cards_raw)))

        self.__mechanics = list(set(jmespath.search(expression="*[?type!='Enchantment'][].mechanics[].name",
                                                    data=en_cards_raw)))
        self.__mechanics.extend(self.__additional_mechanics)

        ru_connection = HsApiConnection(endpoint, locale='ruRU')
        self.__writer('Cards (RU): API request...')
        ru_cards_raw = ru_connection.get()
        self.__writer('Cards (RU): data cleaning...')
        filter_ru_cards = "*[?type!='Enchantment'][].{cardId: cardId, name: name, text: text, flavor: flavor}"
        self.__ru_cards = jmespath.search(expression=filter_ru_cards, data=ru_cards_raw)

    def __get_auxiliary_entities(self):
        """ Формирует вспомогательные данные """
        info_connection = HsApiConnection('info', locale='enUS')
        self.__info = info_connection.get()
        self.__card_classes = jmespath.search(expression='classes', data=self.__info)
        self.__tribes = jmespath.search(expression='races', data=self.__info)

    def __clear_database(self):
        """ Удаляет все карты Hearthstone из БД """
        if self.__rewrite:
            RealCard.objects.all().delete()

    def __write_classes(self):
        """ Записывает в БД отсутствующие классы """
        with open(settings.MODEL_TRANSLATION_FILE, 'r', encoding='utf-8') as f:
            translations = json.load(f)
            for cls in tqdm(self.__card_classes, desc='Classes', ncols=100):
                if CardClass.objects.filter(service_name=cls).exists():
                    continue
                card_class = CardClass(name=cls, service_name=cls)
                card_class.name_ru = translations['classes'].get(cls, card_class.name)
                card_class.save()

    @staticmethod
    def __update_classes():
        """ Обновляет данные классов на основе записанных карт """
        for cls in tqdm(CardClass.objects.all(), desc='Updating class data...', ncols=100):
            if RealCard.objects.filter(collectible=True, card_class=cls).exists():
                cls.collectible = True
                cls.save()

    def __write_tribes(self):
        """ Записывает в БД отсутствующие расы """
        with open(settings.MODEL_TRANSLATION_FILE, 'r', encoding='utf-8') as f:
            translations = json.load(f)
            for t in tqdm(self.__tribes, desc='Tribes', ncols=100):
                if Tribe.objects.filter(service_name=t).exists():
                    continue
                tribe = Tribe(name=t, service_name=t)
                tribe.name_ru = translations['tribes'].get(t, tribe.name)
                tribe.save()

    def __write_sets(self):
        """ Записывает в БД отсутствующие наборы карт """
        with open(settings.MODEL_TRANSLATION_FILE, 'r', encoding='utf-8') as f:
            translations = json.load(f)
            for s in tqdm(self.__card_sets, desc='Addons', ncols=100):
                if CardSet.objects.filter(service_name=s).exists():
                    continue
                card_set = CardSet(name=s, service_name=s)
                card_set.name_ru = translations['sets'].get(s, card_set.name)
                card_set.save()

            if not CardSet.objects.filter(service_name='unknown').exists():
                unknown_set = CardSet(name='unknown', service_name='unknown')
                unknown_set.name_ru = translations['sets'].get('unknown', unknown_set.name)
                unknown_set.save()

    def __write_mechanics(self):
        """ Записывает в БД отсутствующие механики карт """
        with open(settings.MODEL_TRANSLATION_FILE, 'r', encoding='utf-8') as f:
            translations = json.load(f)
            for t in tqdm(self.__mechanics, desc='Mechanics', ncols=100):
                if Mechanic.objects.filter(service_name=t).exists():
                    continue
                mech_translation = translations['mechanics'].get(t)
                name_en = translations['mechanics'][t]['enUS'] if mech_translation else t
                mechanic = Mechanic(name=name_en, service_name=t)
                mechanic.name_ru = translations['mechanics'][t]['ruRU'] if mech_translation else t
                if t in self.__hidden_mechanics:
                    mechanic.hidden = True
                mechanic.save()

    @staticmethod
    def __write_formats():
        """ Записывает в БД отсутствующие форматы игры """
        with open(settings.MODEL_TRANSLATION_FILE, 'r', encoding='utf-8') as f:
            translations = json.load(f)
            for fmt in tqdm(translations['formats'], desc='Formats', ncols=100):
                if Format.objects.filter(numerical_designation=fmt['num']).exists():
                    continue
                format_ = Format(numerical_designation=fmt['num'], name=fmt['name_en'])
                format_.name_ru = fmt['name_ru']
                format_.save()

    @staticmethod
    def __align_card_type(type_name: str) -> str:
        """ Возвращает соответствующий тип карты, как он определен в модели """
        return C_TYPES.get(type_name.lower(), RealCard.CardTypes.UNKNOWN)

    @staticmethod
    def __align_rarity(rarity_name: str) -> str:
        """ Возвращает соответствующую редкость, как она определена в модели """
        return RARITIES.get(rarity_name.lower(), RealCard.Rarities.UNKNOWN)

    @staticmethod
    def __align_spellschool(spellschool: str):
        """ Возвращает соответствующий тип заклинания, как он определен в модели """
        return SPELL_SCHOOLS.get(spellschool.lower(), RealCard.SpellSchools.UNKNOWN)

    @staticmethod
    def __write_set_to_card(r_card: RealCard, j_card: dict):
        """ Связывает карту с набором (FK) """
        try:
            base_set = CardSet.objects.get(service_name=j_card.get('cardSet'))
        except CardSet.DoesNotExist:
            base_set = CardSet.objects.get(service_name='unknown')
        r_card.card_set = base_set

    def __write_mechanics_to_card(self, r_card: RealCard, j_card: dict):
        """ Связывает карту с механиками (m2m) """

        for m in self.__additional_mechanics:
            if m in r_card.text:
                r_card.mechanic.add(Mechanic.objects.get(service_name=m))

        if 'mechanics' not in j_card:
            return

        mechanics = [m['name'] for m in j_card['mechanics']]
        for m in mechanics:
            r_card.mechanic.add(Mechanic.objects.get(service_name=m))


    @staticmethod
    def __write_classes_to_card(r_card: RealCard, j_card: dict):
        """ Связывает карту с классами (m2m) """
        if 'classes' in j_card:
            for cls in j_card['classes']:
                r_card.card_class.add(CardClass.objects.get(service_name=cls))
        elif 'playerClass' in j_card:
            r_card.card_class.add(CardClass.objects.get(service_name=j_card['playerClass']))

    @staticmethod
    def __write_tribe_to_card(r_card: RealCard, j_card: dict):
        """ Связывает карту с расами (m2m) """
        if 'race' in j_card:
            r_card.tribe.add(Tribe.objects.get(service_name=j_card['race']))

    def __write_cards(self):
        """ Обновляет карты в БД """
        for j_card in tqdm(self.__en_cards, desc='Cards', ncols=100):
            if all([not self.__rewrite,
                    (r_card_queryset := RealCard.objects.filter(card_id=j_card['cardId'])).exists(),
                    self.__is_equivalent(r_card_queryset.first(), j_card)]):
                continue
            r_card, created = RealCard.objects.get_or_create(
                card_id=j_card['cardId'],
                dbf_id=int(j_card['dbfId'])
            )
            r_card.name = j_card['name']
            r_card.service_name = r_card.name.upper()
            r_card.card_type = self.__align_card_type(j_card.get('type', ''))
            r_card.cost = int(j_card.get('cost', 0))
            r_card.attack = int(j_card.get('attack', 0))
            r_card.health = int(j_card.get('health', 0))
            r_card.durability = int(j_card.get('durability', 0))
            r_card.armor = int(j_card.get('armor', 0))
            r_card.text = clear_unreadable(j_card.get('text', ''))
            r_card.flavor = clear_unreadable(j_card.get('flavor', ''))
            r_card.rarity = self.__align_rarity(j_card.get('rarity', ''))
            r_card.spell_school = self.__align_spellschool(j_card.get('spellSchool', ''))
            r_card.slug = f'{slugify(r_card.name)}-{str(r_card.dbf_id)}'

            if created:
                r_card.author = 'Blizzard'
                r_card.artist = j_card.get('artist', '')
                r_card.collectible = j_card.get('collectible', False)
                r_card.battlegrounds = r_card.card_set == 'Battlegrounds'

                image_en_path = f'cards/en/{r_card.card_id}.png'
                image_ru_path = f'cards/ru/{r_card.card_id}.png'
                thumbnail_path = f'cards/thumbnails/{r_card.card_id}.png'
                if (settings.MEDIA_ROOT / image_en_path).is_file():
                    r_card.image_en = image_en_path
                if (settings.MEDIA_ROOT / image_ru_path).is_file():
                    r_card.image_ru = image_ru_path
                if (settings.MEDIA_ROOT / thumbnail_path).is_file():
                    r_card.thumbnail = thumbnail_path

                self.__write_set_to_card(r_card, j_card)

            # Перевод карты на русский
            j_card_ru = self.__extract_ru_card('cardId', r_card.card_id)
            # KeyError исключено - j_card_ru гарантированно имеет искомые ключи
            r_card.name_ru = j_card_ru['name']
            r_card.text_ru = clear_unreadable(j_card_ru['text'])
            r_card.flavor_ru = clear_unreadable(j_card_ru['flavor'])

            r_card.save()

            # Заполнение ManyToMany-полей
            self.__write_mechanics_to_card(r_card, j_card)
            self.__write_classes_to_card(r_card, j_card)
            self.__write_tribe_to_card(r_card, j_card)

    def __is_equivalent(self, r_card: RealCard, j_card: dict) -> bool:
        """ Проверяет, была ли карта понерфлена """

        if not r_card:
            return False

        equivalent = all([r_card.name == j_card['name'],
                          r_card.text == clear_unreadable(j_card.get('text', '')),
                          r_card.spell_school == self.__align_spellschool(j_card.get('spellSchool', '')),
                          r_card.cost == int(j_card.get('cost', 0)),
                          r_card.attack == int(j_card.get('attack', 0)),
                          r_card.health == int(j_card.get('health', 0)),
                          r_card.durability == int(j_card.get('durability', 0)),
                          r_card.armor == int(j_card.get('armor', 0))])
        if not equivalent and r_card.collectible:
            self.to_be_updated.append(r_card.card_id)

        return equivalent

    def __extract_ru_card(self, key: str, value) -> dict:
        """ Извлекает карту-словарь из списка ru_cards """
        for index, d in enumerate(self.__ru_cards):
            if d[key] == value:
                return self.__ru_cards.pop(index)
        return {}

    def __rebuild_decks(self):
        """ Пересборка существующих колод после обновления данных о картах """
        if not self.__rewrite:
            return

        for deck in tqdm(Deck.objects.all(), desc='Rebuilding decks', ncols=100):
            cards, heroes, format_ = parse_deckstring(deck.string)
            deck.deck_class = RealCard.objects.get(dbf_id=heroes[0]).card_class.all().first()
            deck.deck_format = Format.objects.get(numerical_designation=format_)
            deck.save()
            for dbf_id, number in cards:
                card = RealCard.includibles.get(dbf_id=dbf_id)
                ci = Inclusion(deck=deck, card=card, number=number)
                ci.save()
                deck.cards.add(card)

    def update(self):
        """ Выполняет обновление БД """

        with transaction.atomic():
            if self.__rewrite:
                self.__clear_database()
            self.__write_classes()
            self.__write_tribes()
            self.__write_sets()
            self.__write_formats()
            self.__write_mechanics()
            self.__write_cards()
            self.__update_classes()
            self.__rebuild_decks()


def clear_unreadable(text: str) -> str:
    """ Избавляет текст от нечитаемых символов и прочего мусора """

    if text is None:
        return ''

    new_text = re.sub(r'\\n', ' ', text)
    new_text = re.sub(r'-\[x]__', '', new_text)
    new_text = re.sub(r'\[x]', '', new_text)
    new_text = re.sub(r'\$', '', new_text)
    new_text = re.sub(r'_', ' ', new_text)
    new_text = re.sub(r'@', '0', new_text)
    return new_text
