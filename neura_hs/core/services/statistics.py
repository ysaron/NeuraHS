from collections import namedtuple
from django.db.models import Count
from django.utils.translation import gettext_lazy as _

from gallery.models import RealCard, FanCard
from decks.models import Deck, Format

StatisticsItem = namedtuple('StatisticsItem', ['label', 'value'])
StatisticsList = namedtuple('StatisticsList', ['label', 'lst'])


def get_fancard_statistics() -> list[StatisticsItem]:
    num_fancards = FanCard.objects.count()
    num_leg_fancards = FanCard.objects.search_by_rarity(RealCard.Rarities.LEGENDARY).count()

    return [StatisticsItem(_('Total'), num_fancards),
            StatisticsItem(_('Legendary'), num_leg_fancards)]


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

    return [StatisticsItem(_('Total'), num_realcards),
            StatisticsItem(_('Collectible'), num_realcards_coll),
            StatisticsItem(_('Legendary'), num_realcards_leg),
            StatisticsItem(_('Epic'), num_realcards_epic),
            StatisticsItem(_('Rare'), num_realcards_rare),
            StatisticsItem(_('Common'), num_realcards_common),
            StatisticsItem(_('Has BattleCry'), num_realcards_bc),
            StatisticsItem(_('Has DeathRattle'), num_realcards_dr),
            StatisticsItem(_('Has LifeSteal'), num_realcards_lf),
            StatisticsItem(_('Spells'), num_realcards_spells)]


def get_deck_statistics() -> list[StatisticsItem]:

    decks = Deck.nameless.annotate(num_unique_cards=Count('cards'))
    num_all = decks.count()
    num_standard = decks.filter(deck_format__numerical_designation=2).count()
    num_wild = decks.filter(deck_format__numerical_designation=1).count()
    num_classic = decks.filter(deck_format__numerical_designation=3).count()
    num_highlander = decks.filter(num_unique_cards=30).count()

    return [StatisticsItem(_('Total'), num_all),
            StatisticsItem(_('Standard'), num_standard),
            StatisticsItem(_('Wild'), num_wild),
            StatisticsItem(_('Classic'), num_classic),
            StatisticsItem(_('Highlander'), num_highlander)]


def get_statistics_context() -> dict:
    context = {}
    context |= {'fancards': StatisticsList(_('Fan cards'), get_fancard_statistics())}
    context |= {'realcards': StatisticsList(_('HS cards'), get_realcard_statistics())}
    context |= {'decks': StatisticsList(_('Decks'), get_deck_statistics())}

    return context
