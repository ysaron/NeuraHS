from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.conf import settings
from django.db import transaction
import json
import jmespath
import requests
import re
from tqdm import tqdm
from datetime import datetime

from core.services.deck_codes import parse_deckstring
from ...models import RealCard, CardClass, Tribe, CardSet
from decks.models import Deck, Format, Inclusion

locale_list = ['enUS', 'ruRU']
endpoint_list = ['info', 'cards']
rewrite_help_msg = 'Rewrite cards and rebuild decks. Use in case of changing existing cards'


class Command(BaseCommand):
    help = 'Update the card database'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rewrite: bool = False

    def add_arguments(self, parser):
        parser.add_argument('-r', '--rewrite', action='store_true', help=rewrite_help_msg)

    def handle(self, *args, **options):

        start = datetime.now()

        self.rewrite = options['rewrite']

        api = HsApiWorker(host=settings.HSAPI_HOST, token=settings.X_RAPIDARI_KEY)
        self.stdout.write('API request: enUS cards...')
        en_cards = api.get_data(endpoint='cards', locale='enUS')
        self.stdout.write('API request: ruRU cards...')
        ru_cards = api.get_data(endpoint='cards', locale='ruRU')
        self.stdout.write('API request: current Hearthstone state...')
        info = api.get_data(endpoint='info', locale='enUS')

        # создание списка подлежащих записи карт из JSON
        en_cards_line: list[dict] = jmespath.search(expression="*[?type!='Enchantment'][]", data=en_cards)
        ru_cards_line: list[dict] = jmespath.search(expression="*[?type!='Enchantment'][]", data=ru_cards)

        card_classes: list = jmespath.search(expression='classes', data=info)
        tribes: list = jmespath.search(expression='races', data=info)
        card_sets: list = list(set(jmespath.search(expression="*[?type!='Enchantment'][].cardSet", data=en_cards)))

        base = DbWorker(en_cards=en_cards_line, ru_cards=ru_cards_line, card_classes=card_classes,
                        tribes=tribes, card_sets=card_sets)

        with transaction.atomic():
            if self.rewrite:
                self.stdout.write('Removing obsolete data...')
                base.clear_db()
            base.write_card_classes()
            base.write_tribes()
            base.write_card_sets()
            base.write_formats()
            base.write_en_cards(self.rewrite)
            base.add_ru_translation()
            base.update_card_classes()
            if self.rewrite:
                base.rebuild_decks()

        end = datetime.now() - start
        self.stdout.write(f'Database update took {end.seconds}s')


class DbWorker:

    translations = settings.MODEL_TRANSLATION_FILE

    def __init__(self, en_cards, ru_cards, card_classes, tribes, card_sets):
        self.en_cards = en_cards
        self.ru_cards = ru_cards
        self.card_classes = card_classes
        self.tribes = tribes
        self.card_sets = card_sets

    @staticmethod
    def clear_db():
        RealCard.objects.all().delete()

    def write_card_classes(self):
        """ Записывает существующие игровые классы (en + ru) """
        with open(DbWorker.translations, 'r', encoding='utf-8') as f:
            translations = json.load(f)
            for cls in tqdm(self.card_classes, desc='Classes', ncols=100):
                if CardClass.objects.filter(service_name=cls).exists():
                    continue
                card_class = CardClass(name=cls, service_name=cls)
                card_class.name_ru = translations['classes'].get(cls, card_class.name)
                card_class.save()

    @staticmethod
    def update_card_classes():
        """ Обновляет данные классов на основе записанных карт """
        for cls in tqdm(CardClass.objects.all(), desc='Updating class data...', ncols=100):
            if RealCard.objects.filter(collectible=True, card_class=cls).exists():
                cls.collectible = True
                cls.save()

    def write_tribes(self):
        """ Записывает существующие расы существ (en + ru) """
        with open(DbWorker.translations, 'r', encoding='utf-8') as f:
            translations = json.load(f)
            for t in tqdm(self.tribes, desc='Tribes', ncols=100):
                if Tribe.objects.filter(service_name=t).exists():
                    continue
                tribe = Tribe(name=t, service_name=t)
                tribe.name_ru = translations['tribes'].get(t, tribe.name)
                tribe.save()

    def write_card_sets(self):
        """ Записывает существующие наборы карт (en + ru) """
        with open(DbWorker.translations, 'r', encoding='utf-8') as f:
            translations = json.load(f)
            for s in tqdm(self.card_sets, desc='Addons', ncols=100):
                if CardSet.objects.filter(service_name=s).exists():
                    continue
                card_set = CardSet(name=s, service_name=s)
                card_set.name_ru = translations['sets'].get(s, card_set.name)
                card_set.save()

            if not CardSet.objects.filter(service_name='unknown').exists():
                unknown_set = CardSet(name='unknown', service_name='unknown')
                unknown_set.name_ru = translations['sets'].get('unknown', unknown_set.name)
                unknown_set.save()

    @staticmethod
    def write_formats():
        """  """
        with open(DbWorker.translations, 'r', encoding='utf-8') as f:
            translations = json.load(f)
            for fmt in tqdm(translations['formats'], desc='Formats', ncols=100):
                if Format.objects.filter(numerical_designation=fmt['num']).exists():
                    continue
                format_ = Format(numerical_designation=fmt['num'], name=fmt['name_en'])
                format_.name_ru = fmt['name_ru']
                format_.save()

    def write_en_cards(self, rewrite):
        for j_card in tqdm(self.en_cards, desc='Cards (enUS)', ncols=100):
            if not rewrite:    # только что очищенную таблицу нет смысла проверять на содержание записи
                if RealCard.objects.filter(card_id=j_card['cardId']).exists():
                    continue
            r_card = RealCard()
            r_card.name = j_card['name']
            r_card.service_name = r_card.name.upper()
            r_card.author = 'Blizzard'
            r_card.card_type = align_card_type(j_card.get('type', ''))
            r_card.cost = int(j_card.get('cost', 0))
            r_card.attack = int(j_card.get('attack', 0))
            r_card.health = int(j_card.get('health', 0))
            r_card.durability = int(j_card.get('durability', 0))
            r_card.armor = int(j_card.get('armor', 0))
            r_card.text = clear_unreadable(j_card.get('text', ''))
            r_card.flavor = clear_unreadable(j_card.get('flavor', ''))
            r_card.rarity = align_rarity(j_card.get('rarity', ''))
            r_card.spell_school = align_spellschool(j_card.get('spellSchool', ''))

            r_card.card_id = j_card['cardId']
            r_card.dbf_id = int(j_card['dbfId'])
            r_card.artist = j_card.get('artist', '')
            r_card.collectible = j_card.get('collectible', False)
            r_card.slug = f'{slugify(r_card.name)}-{str(r_card.dbf_id)}'

            r_card.battlegrounds = r_card.card_set == 'Battlegrounds'

            self.write_mechanics_to_card(r_card, j_card)
            self.write_set_to_card(r_card, j_card)

            r_card.save()

            # Заполнение ManyToMany-полей
            self.write_classes_to_card(r_card, j_card)
            self.write_tribe_to_card(r_card, j_card)

    @staticmethod
    def write_mechanics_to_card(card: RealCard, data: dict):
        """ Заполняет поля механик карты """

        if 'mechanics' not in data:
            return

        mechanics = [m['name'].lower() for m in data['mechanics']]
        card.silence = 'silence' in mechanics
        card.battlecry = 'battlecry' in mechanics
        card.divine_shield = 'divine shield' in mechanics
        card.stealth = 'stealth' in mechanics
        card.overload = 'overload' in mechanics
        card.windfury = 'windfury' in mechanics
        card.secret = 'secret' in mechanics
        card.charge = 'charge' in mechanics
        card.deathrattle = 'deathrattle' in mechanics
        card.taunt = 'taunt' in mechanics
        card.spell_damage = 'spell damage' in mechanics
        card.combo = 'combo' in mechanics
        card.aura = 'aura' in mechanics
        card.poison = 'poisonous' in mechanics
        card.freeze = 'freeze' in mechanics
        card.rush = 'rush' in mechanics
        card.spell_immune = 'immunetospellpower' in mechanics
        card.lifesteal = 'lifesteal' in mechanics
        card.casts_when_drawn = 'casts when drawn' in mechanics
        card.inspire = 'inspire' in mechanics
        card.spell_burst = 'spellburst' in mechanics
        card.discover = 'discover' in mechanics
        card.echo = 'echo' in mechanics
        card.quest = 'quest' in mechanics
        card.side_quest = 'sidequest' in mechanics
        card.one_turn_effect = 'oneturneffect' in mechanics
        card.reborn = 'reborn' in mechanics
        card.outcast = 'outcast' in mechanics
        card.magnetic = 'magnetic' in mechanics
        card.recruit = 'recruit' in mechanics
        card.corrupt = 'corrupt' in mechanics
        card.twinspell = 'twinspell' in mechanics
        card.jade_golem = 'jade golem' in mechanics
        card.adapt = 'adapt' in mechanics
        card.overkill = 'overkill' in mechanics
        card.invoke = 'invoke' in mechanics
        card.blood_gem = 'blood gem' in mechanics
        card.frenzy = 'frenzy' in mechanics
        card.tradeable = 'tradeable' in mechanics
        card.questline = 'questline' in mechanics
        # card.dormant = 'dormant' in j_card['name'].lower()

    def add_ru_translation(self):
        """ Добавляет полям 'name', 'text' и 'flavor' карт перевод на русский """
        for j_card in tqdm(self.ru_cards, desc='ruRU translation', ncols=100):
            card_id = j_card['cardId']
            r_card = RealCard.objects.get(card_id=card_id)
            r_card.name_ru = j_card['name']
            r_card.text_ru = clear_unreadable(j_card.get('text', ''))
            r_card.flavor_ru = clear_unreadable(j_card.get('flavor', ''))
            r_card.save()

    @staticmethod
    def write_set_to_card(card: RealCard, data: dict):
        """ Связывает карту с набором (FK) """
        try:
            base_set = CardSet.objects.get(service_name=data.get('cardSet'))
        except CardSet.DoesNotExist:
            base_set = CardSet.objects.get(service_name='unknown')
        card.card_set = base_set

    @staticmethod
    def write_classes_to_card(card: RealCard, data: dict):
        """ Связывает карту с классами (m2m) """
        if 'classes' in data:
            for cls in data['classes']:
                card.card_class.add(CardClass.objects.get(service_name=cls))
        elif 'playerClass' in data:
            card.card_class.add(CardClass.objects.get(service_name=data['playerClass']))

    @staticmethod
    def write_tribe_to_card(card: RealCard, data: dict):
        """ Связывает карту с расами (m2m) """
        if 'race' in data:
            card.tribe.add(Tribe.objects.get(service_name=data['race']))

    @staticmethod
    def rebuild_decks():
        """  """
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


class HsApiWorker:
    """ Класс для работы с Hearthstone API """

    def __init__(self, host: str, token: str):
        self.headers = {'x-rapidapi-key': token, 'x-rapidapi-host': host}
        self.params = {}

    @staticmethod
    def check_endpoint(endpoint: str) -> None:
        if endpoint not in endpoint_list:
            raise ValueError(f'Endpoint must be one of {endpoint_list}')

    @staticmethod
    def check_locale(loc: str) -> None:
        if loc not in locale_list:
            raise ValueError(f'Locale must be one of {locale_list}')

    def get_data(self, endpoint: str, locale: str = 'enUS'):
        """
        Делает запрос определенных данных из API, возвращает JSON
        :param endpoint: cards / info
        :param locale: enUS / ruRU
        :return: JSON-данные
        """
        self.check_endpoint(endpoint)
        self.check_locale(locale)
        url = settings.HSAPI_BASEURL + endpoint.lower()
        r = requests.get(url=url, headers=self.headers, params={'locale': locale}, stream=True)
        r.raise_for_status()
        return r.json()


def align_card_type(type_name: str) -> str:
    """ Возвращает соответствующий тип карты, как он определен в модели """
    d = {'minion': RealCard.CardTypes.MINION,
         'spell': RealCard.CardTypes.SPELL,
         'weapon': RealCard.CardTypes.WEAPON,
         'hero': RealCard.CardTypes.HERO,
         'hero power': RealCard.CardTypes.HEROPOWER}

    return d.get(type_name.lower(), RealCard.CardTypes.UNKNOWN)


def align_rarity(rarity_name: str) -> str:
    """ Возвращает соответствующую редкость, как она определена в модели """

    d = {'free': RealCard.Rarities.NO_RARITY,
         'common': RealCard.Rarities.COMMON,
         'rare': RealCard.Rarities.RARE,
         'epic': RealCard.Rarities.EPIC,
         'legendary': RealCard.Rarities.LEGENDARY}

    return d.get(rarity_name.lower(), RealCard.Rarities.UNKNOWN)


def align_spellschool(spellschool: str):
    """ Возвращает соответствующий тип заклинания, как он определен в модели """

    d = {'holy': RealCard.SpellSchools.HOLY,
         'shadow': RealCard.SpellSchools.SHADOW,
         'nature': RealCard.SpellSchools.NATURE,
         'fel': RealCard.SpellSchools.FEL,
         'fire': RealCard.SpellSchools.FIRE,
         'frost': RealCard.SpellSchools.FROST,
         'arcane': RealCard.SpellSchools.ARCANE}

    return d.get(spellschool.lower(), RealCard.SpellSchools.UNKNOWN)


def clear_unreadable(text: str) -> str:
    """ Избавляет текст от нечитаемых символов и прочего мусора"""
    new_text = re.sub(r'\\n', ' ', text)
    new_text = re.sub(r'-\[x]__', '', new_text)
    new_text = re.sub(r'\[x]', '', new_text)
    new_text = re.sub(r'\$', '', new_text)
    new_text = re.sub(r'_', ' ', new_text)
    new_text = re.sub(r'@', '0', new_text)
    return new_text
