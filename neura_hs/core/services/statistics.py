from collections import namedtuple

from gallery.models import RealCard, FanCard
from decks.models import Deck, Format

StatisticsItem = namedtuple('StatisticsItem', ['label', 'value'])
StatisticsList = namedtuple('StatisticsList', ['label', 'lst'])


def get_fancard_statistics() -> list[StatisticsItem]:
    num_fancards = FanCard.objects.count()
    num_leg_fancards = FanCard.objects.search_by_rarity(RealCard.Rarities.LEGENDARY).count()

    return [StatisticsItem('Всего', num_fancards),
            StatisticsItem('Легендарные', num_leg_fancards)]


def get_realcard_statistics() -> list[StatisticsItem]:
    num_realcards = RealCard.objects.count()
    collectibles = RealCard.objects.search_collectible(True)
    num_realcards_coll = collectibles.count()
    num_realcards_leg = collectibles.search_by_rarity(RealCard.Rarities.LEGENDARY).count()
    num_realcards_epic = collectibles.search_by_rarity(RealCard.Rarities.EPIC).count()
    num_realcards_rare = collectibles.search_by_rarity(RealCard.Rarities.RARE).count()
    num_realcards_common = collectibles.search_by_rarity(RealCard.Rarities.COMMON).count()
    num_realcards_bc = collectibles.search_by_mechanic(RealCard.Mechanics.BATTLECRY).count()
    num_realcards_dr = collectibles.search_by_mechanic(RealCard.Mechanics.DEATHRATTLE).count()
    num_realcards_lf = collectibles.search_by_mechanic(RealCard.Mechanics.LIFESTEAL).count()
    num_realcards_spells = collectibles.search_by_type(RealCard.CardTypes.SPELL).count()

    return [StatisticsItem('Всего', num_realcards),
            StatisticsItem('Коллекционные', num_realcards_coll),
            StatisticsItem('Легендарные', num_realcards_leg),
            StatisticsItem('Эпические', num_realcards_epic),
            StatisticsItem('Редкие', num_realcards_rare),
            StatisticsItem('Обычные', num_realcards_common),
            StatisticsItem('С "Боевым кличем"', num_realcards_bc),
            StatisticsItem('С "Предсмертным хрипом"', num_realcards_dr),
            StatisticsItem('С "Похищением жизни"', num_realcards_lf),
            StatisticsItem('Заклинания', num_realcards_spells)]


def get_deck_statistics() -> list[StatisticsItem]:
    return [StatisticsItem('...', '......'),
            StatisticsItem('...', '......')]


def get_statistics_context() -> dict:
    context = {}
    context |= {'fancards': StatisticsList('Фан-карты', get_fancard_statistics())}
    context |= {'realcards': StatisticsList('Карты Hearthstone', get_realcard_statistics())}
    context |= {'decks': StatisticsList('Колоды', get_deck_statistics())}

    return context
