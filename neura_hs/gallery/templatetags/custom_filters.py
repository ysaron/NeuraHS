from django import template
from ..models import Card

register = template.Library()


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
        return ''.join(card.card_class.all()[0].name.lower().split())
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
