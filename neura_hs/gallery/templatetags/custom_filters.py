from django import template
from collections import namedtuple
from ..models import Card, FanCard

register = template.Library()
Parameter = namedtuple('Parameter', ['name', 'icon', 'value'])


@register.filter
def get_item(dictionary, key):
    """ Используется в связке с другими фильтрами, возвращающими словарь """
    return dictionary.get(key)


@register.filter(name='verbose_group')
def get_verbose_group(user):
    """ Возвращает имя и стиль отображения группы автора """
    if user.is_superuser:
        return {'group': 'Владелец', 'bg-color': 'bg-success'}

    if user.groups.all()[0].name == 'editor':
        return {'group': 'Редактор', 'bg-color': 'bg-dark'}

    if user.groups.all()[0].name == 'common':
        return {'group': 'Пользователь', 'bg-color': 'bg-primary'}

    return {'group': '', 'bg-color': ''}


@register.filter(name='display')
def get_display_type(fieldname):
    """ Возвращает Bootstrap-класс для сокрытия не подлежащих отображению полей """
    non_displayable_fields = ['author', 'slug', 'state']
    return 'd-none' if fieldname in non_displayable_fields else ''


@register.filter(name='cclass')
def get_cardclass_style(card):
    """ Возвращает CSS-класс оформления области соответствующего Hearthstone-класса """
    if card.card_class.count() == 1:
        return ''.join(card.card_class.all()[0].service_name.lower().split())
    else:
        return 'multiclass'


@register.filter(name='rar')
def get_rarity_style(card):
    """ Возвращает CSS-класс оформления для соответствующей редкости карты """
    matches = {Card.Rarities.LEGENDARY: 'legendary',
               Card.Rarities.EPIC: 'epic',
               Card.Rarities.RARE: 'rare'}
    return matches.get(card.rarity, 'common')


@register.filter(name='coll_name_fmt')
def get_formatted_name(card):
    """ Возвращает название карты, отформатированное в зависимости от коллекционности """
    return card.name if card.collectible else f'[{card.name}]'


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
