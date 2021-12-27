import pytest
from decks.models import Deck
from gallery.models import CardClass, CardSet, Tribe, RealCard, FanCard
from gallery.management.commands.hs_base_update import DbWorker
from slugify import slugify


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
    def get_real_card(name: str, card_id: str, dbf_id: int):
        card = RealCard.objects.create(
            name=name,
            slug=f'{slugify(name)}-{dbf_id}',
            card_type=RealCard.CardTypes.MINION,
            cost=7,
            attack=9,
            health=6,
            text='Battlecry: does nothing',
            flavor='Some test flavor',
            rarity=RealCard.Rarities.EPIC,
            card_set=CardSet.objects.get_or_create(**card_set(name='Scholomance Academy'))[0],
            card_id=card_id,
            dbf_id=dbf_id,
            collectible=True
        )
        card.card_class.add(CardClass.objects.get_or_create(**card_class(name='Rogue'))[0])
        card.tribe.add(Tribe.objects.get_or_create(**tribe(name='Beast'))[0])
        return card

    return get_real_card


@pytest.fixture
def fan_card():
    pass


@pytest.fixture
def hs_db_worker(en_cards, ru_cards, card_classes, tribes, card_sets):
    return DbWorker(en_cards, ru_cards, card_classes, tribes, card_sets)


@pytest.fixture
def deckstring():
    return 'AAECAaHDAwb1zgOj0QOd2AO/4AOP5AOJiwQM5boD6LoD77oDm84D8NQDieADiuADpOED0eEDiuQDjOQDr4AEAA=='


@pytest.fixture
def deckstring2():
    return 'AAEBAaIHBq8QmxSRvAKA0wL+mgOs6wMMm8gC5dEC6vMC+5oDragDqssDiNADpNED99QDkp8E7qAE+6UEAA=='


@pytest.fixture
def deck_data():
    return (
        [(59253, 1), (59555, 1), (60445, 1), (61503, 1), (61967, 1), (66953, 1),
         (56677, 2), (56680, 2), (56687, 2), (59163, 2), (60016, 2), (61449, 2),
         (61450, 2), (61604, 2), (61649, 2), (61962, 2), (61964, 2), (65583, 2)],
        [57761],
        2
    )


@pytest.fixture
def deck(db, hs_db_worker, real_card):
    data = [
        ('Deadly Poison', 'CORE_CS2_074', 69522),
        ('Hallucination', 'UNG_856', 42011),
        ('Paralytic Poison', 'BAR_321', 62892),
        ('Patches the Pirate', 'CFM_637', 40465),
        ('Secret Passage', 'SCH_305', 58794),
        ('Swashburglar', 'CORE_KAR_069', 69742),
        ('Wand Thief', 'SCH_350', 59556),
        ('Cavern Shinyfinder', 'LOOT_033', 43237),
        ('Clever Disguise', 'ULD_328', 54317),
        ('Underbelly Fence', 'DAL_714', 52603),
        ('Beneath the Grounds', 'AT_035', 2587),
        ('Vulpera Toxinblade', 'SCH_519', 59400),
        ('Spectral Cutlass', 'GIL_672', 47594),
        ("Tinker's Sharpsword Oil", 'GVG_022', 2095),
        ('Vendetta', 'DAL_716', 52606),
        ('Cutting Class', 'SCH_623', 60023),
        ('Wildpaw Gnoll', 'AV_298', 70395),
        ('Valeera the Hollow', 'ICC_827', 43392),
        ('Valeera Sanguinar', 'HERO_03', 930),
    ]
    hs_db_worker.write_formats()
    for name, card_id, dbf_id in data:
        real_card(name, card_id, dbf_id)
