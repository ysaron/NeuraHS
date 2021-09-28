from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.conf import settings
import jmespath
import requests
import re
from datetime import datetime

from ...models import RealCard, CardClass, Tribe, CardSet

locale_list = ['enUS', 'ruRU']
endpoint_list = ['info', 'cards']


class Command(BaseCommand):
    help = 'Update the card database'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rewrite: bool = False

    def add_arguments(self, parser):
        parser.add_argument('-r', '--rewrite', action='store_true', help='rewrite the entire table')

    def handle(self, *args, **options):

        start = datetime.now()

        self.rewrite = options['rewrite']
        if self.rewrite:
            RealCard.objects.all().delete()

        api = HsApiWorker(host=settings.HSAPI_HOST, token=settings.X_RAPIDARI_KEY)
        en_cards = api.get_data(endpoint='cards', locale='enUS')
        # ru_cards = api.get_data(endpoint='cards', locale='ruRU')

        info = api.get_data(endpoint='info', locale='enUS')

        # создание списка подлежащих записи карт из JSON
        en_cards_line: list[dict] = jmespath.search(expression="*[?type!='Enchantment'][]", data=en_cards)

        card_classes: list = jmespath.search(expression='classes', data=info)
        tribes: list = jmespath.search(expression='races', data=info)
        card_sets: list = list(set(jmespath.search(expression="*[?type!='Enchantment'][].cardSet", data=en_cards)))

        self.write_card_classes(card_classes)
        self.write_tribes(tribes)
        self.write_card_sets(card_sets)

        for index, j_card in enumerate(en_cards_line):
            if not self.rewrite:    # только что очищенную таблицу нет смысла проверять на содержание записи
                if RealCard.objects.filter(card_id=j_card['cardId']).exists():
                    continue
            r_card = RealCard()
            r_card.name = j_card['name']
            r_card.service_name = r_card.name.upper()
            r_card.author = 'Blizzard'
            r_card.card_type = self.align_card_type(j_card.get('type', ''))
            r_card.cost = int(j_card.get('cost', 0))
            r_card.attack = int(j_card.get('attack', 0))
            r_card.health = int(j_card.get('health', 0))
            r_card.durability = int(j_card.get('durability', 0))
            r_card.armor = int(j_card.get('armor', 0))
            r_card.text = clear_unreadable(j_card.get('text', ''))
            r_card.flavor = clear_unreadable(j_card.get('flavor', ''))
            r_card.rarity = self.align_rarity(j_card.get('rarity', ''))
            r_card.spell_school = self.align_spellschool(j_card.get('spellSchool', ''))

            r_card.card_id = j_card['cardId']
            r_card.dbf_id = int(j_card['dbfId'])
            r_card.artist = j_card.get('artist', '')
            r_card.collectible = j_card.get('collectible', False)
            r_card.slug = f'{slugify(r_card.name)}-{str(r_card.dbf_id)}'

            r_card.battlegrounds = r_card.card_set == 'Battlegrounds'

            # Заполнение полей механик
            if 'mechanics' in j_card:
                mechanics = [m['name'].lower() for m in j_card['mechanics']]
                r_card.silence = 'silence' in mechanics
                r_card.battlecry = 'battlecry' in mechanics
                r_card.divine_shield = 'divine shield' in mechanics
                r_card.stealth = 'stealth' in mechanics
                r_card.overload = 'overload' in mechanics
                r_card.windfury = 'windfury' in mechanics
                r_card.secret = 'secret' in mechanics
                r_card.charge = 'charge' in mechanics
                r_card.deathrattle = 'deathrattle' in mechanics
                r_card.taunt = 'taunt' in mechanics
                r_card.spell_damage = 'spell damage' in mechanics
                r_card.combo = 'combo' in mechanics
                r_card.aura = 'aura' in mechanics
                r_card.poison = 'poisonous' in mechanics
                r_card.freeze = 'freeze' in mechanics
                r_card.rush = 'rush' in mechanics
                r_card.spell_immune = 'immunetospellpower' in mechanics
                r_card.lifesteal = 'lifesteal' in mechanics
                r_card.casts_when_drawn = 'casts when drawn' in mechanics
                r_card.inspire = 'inspire' in mechanics
                r_card.spell_burst = 'spellburst' in mechanics
                r_card.discover = 'discover' in mechanics
                r_card.echo = 'echo' in mechanics
                r_card.quest = 'quest' in mechanics
                r_card.side_quest = 'sidequest' in mechanics
                r_card.one_turn_effect = 'oneturneffect' in mechanics
                r_card.reborn = 'reborn' in mechanics
                r_card.outcast = 'outcast' in mechanics
                r_card.magnetic = 'magnetic' in mechanics
                r_card.recruit = 'recruit' in mechanics
                r_card.corrupt = 'corrupt' in mechanics
                r_card.twinspell = 'twinspell' in mechanics
                r_card.jade_golem = 'jade golem' in mechanics
                r_card.adapt = 'adapt' in mechanics
                r_card.overkill = 'overkill' in mechanics
                r_card.invoke = 'invoke' in mechanics
                r_card.blood_gem = 'blood gem' in mechanics
                r_card.frenzy = 'frenzy' in mechanics
                r_card.tradeable = 'tradeable' in mechanics
                r_card.questline = 'questline' in mechanics
                # r_card.dormant = 'dormant' in j_card['name'].lower()

            try:
                base_set = CardSet.objects.get(name=j_card.get('cardSet'))
            except CardSet.DoesNotExist:
                base_set = CardSet.objects.get(name='unknown')
            r_card.card_set = base_set
            r_card.save()

            # Заполнение ManyToMany-полей
            if 'classes' in j_card:
                for cls in j_card['classes']:
                    r_card.card_class.add(CardClass.objects.get(service_name=cls))
            elif 'playerClass' in j_card:
                r_card.card_class.add(CardClass.objects.get(service_name=j_card['playerClass']))

            if 'race' in j_card:
                r_card.tribe.add(Tribe.objects.get(service_name=j_card['race']))

            if index % 200 == 0:
                print(f'Записано карт: {index}')

        end = datetime.now() - start
        self.stdout.write(f'Затрачено времени: {end.seconds} с')

    @staticmethod
    def align_card_type(type_name: str) -> str:
        """ Возвращает соответствующий тип карты, как он определен в модели """
        d = {'minion': RealCard.CardTypes.MINION,
             'spell': RealCard.CardTypes.SPELL,
             'weapon': RealCard.CardTypes.WEAPON,
             'hero': RealCard.CardTypes.HERO,
             'hero power': RealCard.CardTypes.HEROPOWER}

        return d.get(type_name.lower(), RealCard.CardTypes.UNKNOWN)

    @staticmethod
    def align_rarity(rarity_name: str) -> str:
        """ Возвращает соответствующую редкость, как она определена в модели """

        d = {'free': RealCard.Rarities.NO_RARITY,
             'common': RealCard.Rarities.COMMON,
             'rare': RealCard.Rarities.RARE,
             'epic': RealCard.Rarities.EPIC,
             'legendary': RealCard.Rarities.LEGENDARY}

        return d.get(rarity_name.lower(), RealCard.Rarities.UNKNOWN)

    @staticmethod
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

    def write_card_classes(self, classlist: list):
        """  """
        for cls in classlist:
            if CardClass.objects.filter(name=cls).exists():
                continue
            card_class = CardClass(name=cls, service_name=cls)
            card_class.save()

        self.stdout.write(f'Классы записаны ({len(classlist)})')

    def write_tribes(self, tribelist: list):
        """  """
        for t in tribelist:
            if Tribe.objects.filter(name=t).exists():
                continue
            tribe = Tribe(name=t, service_name=t)
            tribe.save()

        self.stdout.write(f'Расы записаны ({len(tribelist)})')

    def write_card_sets(self, setlist: list):
        """  """
        for s in setlist:
            if CardSet.objects.filter(name=s).exists():
                continue
            card_set = CardSet(name=s)
            card_set.save()

        card_set = CardSet(name='unknown')
        card_set.save()
        self.stdout.write(f'Наборы карт записаны ({len(setlist) + 1})')


class HsApiWorker:
    """ Класс для работы с Hearthstone API """

    def __init__(self, host: str, token: str):
        self.headers = {'x-rapidapi-key': token, 'x-rapidapi-host': host}
        self.params = {}

    @staticmethod
    def check_endpoint(endpoint: str) -> None:
        if endpoint not in endpoint_list:
            raise ValueError(f'endpoint must be one of {endpoint_list}')

    @staticmethod
    def check_locale(loc: str) -> None:
        if loc not in locale_list:
            raise ValueError(f'locale must be one of {locale_list}')

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


def clear_unreadable(text: str) -> str:
    """ Избавляет текст от нечитаемых символов и прочего мусора"""
    new_text = re.sub(r'\\n', ' ', text)
    new_text = re.sub(r'-\[x]__', '', new_text)
    new_text = re.sub(r'\[x]', '', new_text)
    new_text = re.sub(r'\$', '', new_text)
    new_text = re.sub(r'_', ' ', new_text)
    new_text = re.sub(r'@', '0', new_text)
    return new_text
