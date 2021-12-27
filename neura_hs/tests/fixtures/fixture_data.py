import pytest
from gallery.models import CardClass, CardSet, Tribe, RealCard, FanCard
from gallery.management.commands.hs_base_update import DbWorker


@pytest.fixture
def card_class(db):
    def make_card_class(**kwargs):
        kwargs['service_name'] = kwargs['name']
        kwargs['collectible'] = True
        return kwargs
    return make_card_class


@pytest.fixture
def tribe(db):
    def make_tribe(**kwargs):
        kwargs['service_name'] = kwargs['name']
        return kwargs
    return make_tribe


@pytest.fixture
def card_set(db):
    def make_card_set(**kwargs):
        kwargs['service_name'] = kwargs['name']
        return kwargs
    return make_card_set


@pytest.fixture
def mechanics():
    pass


@pytest.fixture
def en_cards():
    return [
        {'name': 'Aya Blackpaw', 'cardSet': 'Mean Streets of Gadgetzan', 'type': 'Minion', 'rarity': 'Legendary',
         'cost': 6, 'attack': 5, 'health': 3, 'text': 'some random text', 'flavor': 'some insignificant flavor',
         'collectible': True, 'classes': ['Druid', 'Rogue', 'Shaman'], 'cardId': 'CFM_902', 'dbfId': '40596',
         'mechanics': [{'name': 'Jade Golem'}, {'name': 'Battlecry'}, {'name': 'Deathrattle'}]},
        {'name': 'Twilight Deceptor', 'cardSet': 'United in Stormwind', 'type': 'Minion', 'rarity': 'Common',
         'cost': 2, 'attack': 2, 'health': 3, 'text': 'some random text', 'flavor': 'some insignificant flavor',
         'collectible': True, 'playerClass': 'Priest', 'cardId': 'SW_444', 'dbfId': '64419',
         'mechanics': [{'name': 'Battlecry'}]},
    ]


@pytest.fixture
def ru_cards():
    return [
        {'name': 'Айя Черная Лапа', 'cardSet': 'Mean Streets of Gadgetzan', 'type': 'Minion', 'rarity': 'Legendary',
         'cost': 6, 'attack': 5, 'health': 3, 'text': 'какой-то текст', 'flavor': 'какой-то текст',
         'collectible': True, 'classes': ['Druid', 'Rogue', 'Shaman'], 'cardId': 'CFM_902', 'dbfId': '40596',
         'mechanics': [{'name': 'Jade Golem'}, {'name': 'Battlecry'}, {'name': 'Deathrattle'}]},
        {'name': 'Сумеречный обманщик', 'cardSet': 'United in Stormwind', 'type': 'Minion', 'rarity': 'Common',
         'cost': 2, 'attack': 2, 'health': 3, 'text': 'какой-то текст', 'flavor': 'какой-то текст',
         'collectible': True, 'playerClass': 'Priest', 'cardId': 'SW_444', 'dbfId': '64419',
         'mechanics': [{'name': 'Battlecry'}]},
    ]


@pytest.fixture
def card_classes():
    return ['Druid', 'Rogue', 'Shaman', 'Priest']


@pytest.fixture
def tribes():
    return ['Beast', 'Demon']


@pytest.fixture
def card_sets():
    return ['Mean Streets of Gadgetzan', 'United in Stormwind']


@pytest.fixture
def real_card(db, card_class, tribe, card_set):
    card = RealCard.objects.create(name='New Test Minion',
                                   slug='new-test-minion-9999999',
                                   card_type=RealCard.CardTypes.MINION,
                                   cost=7,
                                   attack=9,
                                   health=6,
                                   text='Battlecry: does nothing',
                                   flavor='Some test flavor',
                                   rarity=RealCard.Rarities.EPIC,
                                   card_set=CardSet.objects.create(**card_set(name='Scholomance Academy')),
                                   card_id='TEST01_CARDID',
                                   dbf_id=9999999,
                                   collectible=True)
    card.card_class.add(CardClass.objects.create(**card_class(name='Druid')))
    card.tribe.add(Tribe.objects.create(**tribe(name='Beast')))
    return card


@pytest.fixture
def fan_card():
    pass


@pytest.fixture
def hs_db_worker(en_cards, ru_cards, card_classes, tribes, card_sets):
    return DbWorker(en_cards, ru_cards, card_classes, tribes, card_sets)
