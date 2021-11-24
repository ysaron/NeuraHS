from django import template
from collections import namedtuple
from ..models import Card, FanCard, RealCard

register = template.Library()
Parameter = namedtuple('Parameter', ['name', 'icon', 'value'])

DeckCards = list[tuple[RealCard, int]]      # алиас для представления карт, составляющих колоду


@register.filter
def get_item(dictionary, key):
    """ Используется в связке с другими фильтрами, возвращающими словарь """
    return dictionary.get(key)


@register.filter(name='verbose_group')
def get_verbose_group(user):
    """ Возвращает имя и стиль отображения группы автора """
    if user.is_superuser:
        return {'group': 'Админ', 'bg-color': 'bg-success', 'background': 'rgba(0, 77, 0, 0.2)'}

    if user.groups.all()[0].name == 'editor':
        return {'group': 'Редактор', 'bg-color': 'bg-dark', 'background': 'rgba(102, 26, 0, 0.2)'}

    if user.groups.all()[0].name == 'common':
        return {'group': 'Пользователь', 'bg-color': 'bg-primary', 'background': 'rgba(0, 0, 102, 0.2)'}

    return {'group': '', 'bg-color': '', 'background': ''}


@register.filter(name='display')
def get_display_type(fieldname):
    """ Возвращает Bootstrap-класс для сокрытия не подлежащих отображению полей """
    non_displayable_fields = ['author', 'slug', 'state']
    return 'd-none' if fieldname in non_displayable_fields else ''


@register.filter(name='cclass')
def get_cardclass_style(card):
    """ Возвращает стили оформления области соответствующего Hearthstone-класса """
    if card.card_class.count() == 0:
        return 'neutral'
    if card.card_class.count() == 1:
        return ''.join(card.card_class.all()[0].service_name.lower().split())
    else:
        lst = [''.join(cls.service_name.lower().split()) for cls in card.card_class.all()]
        return 'multiclass ' + '-'.join(lst)


@register.filter(name='dclass')
def get_deckclass_style(deck):
    """ Возвращает CSS-класс оформления области соответствующего Hearthstone-класса """
    return ''.join(deck.deck_class.service_name.lower().split())


@register.filter(name='rar')
def get_rarity_style(card):
    """ Возвращает CSS-класс оформления для соответствующей редкости карты """
    matches = {Card.Rarities.LEGENDARY: 'legendary',
               Card.Rarities.EPIC: 'epic',
               Card.Rarities.RARE: 'rare'}
    return matches.get(card.rarity, 'common')


@register.inclusion_tag('gallery/tags/stat_cell.html', takes_context=True, name='format_stats')
def format_stats(context, card):
    """ Формирует строку <tr> таблицы card-detail с числовыми параметрами карты """

    svg_path = 'core/images/'
    cost = Parameter('Cost', f'{svg_path}cost.svg', card.cost)

    # карты любого типа имеют, помимо стоимости, максимум 2 параметра, различающихся от типа к типу
    first_param, seconf_param = Parameter(None, None, None), Parameter(None, None, None)

    if card.card_type == Card.CardTypes.MINION:
        first_param = Parameter('Attack', f'{svg_path}attack.svg', card.attack)
        seconf_param = Parameter('Health', f'{svg_path}health.svg', card.health)
    elif card.card_type == Card.CardTypes.WEAPON:
        first_param = Parameter('Attack', f'{svg_path}attack.svg', card.attack)
        seconf_param = Parameter('Durability', f'{svg_path}durability.svg', card.durability)
    elif card.card_type == Card.CardTypes.HERO:
        seconf_param = Parameter('Armor', f'{svg_path}armor.svg', card.armor)

    context.update({'params': [p for p in (cost, first_param, seconf_param) if p.name]})

    return context


@register.filter(name='can_change')
def can_change(user, card: FanCard):
    """ Проверяет, имеет ли пользователь право удалять/редактировать фан-карту """
    return user.is_authenticated and any((card.author == user.author,
                                          user.has_perm('gallery.change_fancard')))


@register.filter(name='craft_cost')
def calc_deck_craft_cost(cards: DeckCards) -> tuple[int, int]:
    """
    Возвращает суммарную стоимость (во внутриигровой валюте)
    создания карт из колоды (в обычном и золотом варианте)
    """
    craft_cost, craft_cost_gold = 0, 0
    rarities = RealCard.Rarities
    prices = {rarities.UNKNOWN: (0, 0),
              rarities.NO_RARITY: (0, 0),
              rarities.COMMON: (40, 400),
              rarities.RARE: (100, 800),
              rarities.EPIC: (100, 1600),
              rarities.LEGENDARY: (1600, 3200)}
    for card in cards:
        craft_cost += prices[card[0].rarity][0] * card[1]
        craft_cost_gold += prices[card[0].rarity][1] * card[1]

    return craft_cost, craft_cost_gold


@register.filter(name='dformat')
def get_format_style(deck) -> str:
    """ Возвращает соответствующий класс стиля формата колоды """
    matching = {0: 'unknown',
                1: 'wild',
                2: 'standard',
                3: 'classic'}
    return matching[deck.deck_format.numerical_designation]


def get_deckcards_stat(cards: DeckCards, field: str) -> list[dict]:
    """
    Возвращает данные о количестве карт в колоде,
    соответствующих различным значением поля field
    """
    lst = []
    result = []
    for card in cards:
        try:
            data = getattr(card[0], field)
        except AttributeError:
            return []   # отразится в шаблоне как отсутствие данных

        if field == 'card_type':
            data = RealCard.CardTypes(data)
        elif field == 'rarity':
            data = RealCard.Rarities(data)

        if data not in lst:
            lst.append(data)
            result.append({'name': data, 'num_cards': card[1]})
        else:
            d = next(stat for stat in result if stat['name'] == data)
            d['num_cards'] += card[1]

    return sorted(result, key=lambda stat: stat['num_cards'], reverse=True)


@register.filter(name='dsetsstat')
def get_deckcards_sets_stat(cards: DeckCards):
    """
    Возвращает данные о наборах карт, используемых в колоде,
    и о кол-ве карт каждого набора
    """
    return get_deckcards_stat(cards, 'card_set')


@register.filter(name='dtypestat')
def get_deckcards_type_stat(cards: DeckCards):
    """ Возвращает данные о типах карт в колоде и кол-ве карт каждого типа """
    return get_deckcards_stat(cards, 'card_type')


@register.filter(name='draritystat')
def get_deckcards_rarity_stat(cards: DeckCards):
    """ Возвращает данные о редкостях карт в колоде и кол-ве карт каждой редкости """
    return get_deckcards_stat(cards, 'rarity')


@register.filter(name='dmechstat')
def get_deckcards_mechanics_stat(cards: DeckCards):
    """
    Возвращает данные о механиках Hearthstone, использующихся
    картами колоды, и о кол-ве этих карт на каждую механику
    """
    # не использует get_deckcards_stat, т.к. карта может иметь более одной механики (отличается логика обработки)
    mechanics = []
    result: list[dict] = []
    for card in cards:
        for mech in card[0].mechanics_list:
            if mech not in mechanics:
                mechanics.append(mech)
                result.append({'name': mech, 'num_cards': card[1]})
            else:
                m = next(m for m in result if m['name'] == mech)
                m['num_cards'] += card[1]

    result.sort(key=lambda mech_: mech_['num_cards'], reverse=True)
    return result


@register.filter(name='setcls')
def set_class_to_form_field(field, css_class: str):
    return field.as_widget(attrs={'class': css_class})
