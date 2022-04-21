from django import template
from django.utils.translation import gettext_lazy as _, to_locale, get_language
from collections import namedtuple
from ..models import Card, FanCard, RealCard

register = template.Library()
Parameter = namedtuple('Parameter', ['name', 'icon', 'value'])


@register.filter
def get_item(dictionary, key):
    """ Используется в связке с другими фильтрами, возвращающими словарь """
    return dictionary.get(key)


@register.filter(name='style_group')
def get_verbose_group(user):
    """ Возвращает имя и стиль отображения группы автора """
    if user.is_superuser:
        return {'group': _('Admin'), 'bg-color': 'bg-success', 'background': 'rgba(0, 77, 0, 0.2)'}

    if user.groups.all()[0].name == 'editor':
        return {'group': _('Editor'), 'bg-color': 'bg-dark', 'background': 'rgba(0, 0, 102, 0.2)'}

    if user.groups.all()[0].name == 'common':
        return {'group': _('User'), 'bg-color': 'bg-primary', 'background': ''}

    return {'group': '', 'bg-color': '', 'background': ''}


@register.filter(name='display')
def get_display_type(fieldname):
    """ Возвращает CSS-стиль для сокрытия не подлежащих отображению полей """
    non_displayable_fields = ['author', 'slug', 'state']
    return 'display: none;' if fieldname in non_displayable_fields else ''


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
    cost = Parameter(_('Cost'), f'{svg_path}cost.svg', card.cost)

    # карты любого типа имеют, помимо стоимости, максимум 2 параметра, различающихся от типа к типу
    first_param, seconf_param = Parameter(None, None, None), Parameter(None, None, None)

    if card.card_type == Card.CardTypes.MINION:
        first_param = Parameter(_('Attack'), f'{svg_path}attack.svg', card.attack)
        seconf_param = Parameter(_('Health'), f'{svg_path}health.svg', card.health)
    elif card.card_type == Card.CardTypes.WEAPON:
        first_param = Parameter(_('Attack'), f'{svg_path}attack.svg', card.attack)
        seconf_param = Parameter(_('Durability'), f'{svg_path}durability.svg', card.durability)
    elif card.card_type == Card.CardTypes.HERO:
        seconf_param = Parameter(_('Armor'), f'{svg_path}armor.svg', card.armor)

    context.update({'params': [p for p in (cost, first_param, seconf_param) if p.name]})

    return context


@register.filter(name='can_change')
def can_change(user, card: FanCard):
    """ Проверяет, имеет ли пользователь право удалять/редактировать фан-карту """
    return user.is_authenticated and any((card.author == user.author,
                                          user.has_perm('gallery.change_fancard')))


@register.filter(name='dformat')
def get_format_style(deck) -> str:
    """ Возвращает соответствующий класс стиля формата колоды """
    matching = {0: 'unknown',
                1: 'wild',
                2: 'standard',
                3: 'classic'}
    return matching[deck.deck_format.numerical_designation]


@register.filter(name='setcls')
def set_class_to_form_field(field, css_class: str):
    return field.as_widget(attrs={'class': css_class})


@register.filter(name='mktitle')
def get_page_title(title: str):
    """ Возвращает заголовок, отображаемый на вкладках """
    return f'{title} | NeuraHS'


@register.filter(name='locale')
def get_locale_name(language_code):
    matches = {'en': 'enUS',
               'ru': 'ruRU'}
    return matches.get(language_code, 'enUS')


@register.filter(name='shortclassname')
def get_short_class_name(deck):
    """ Заменяет слишком длинное название класса на синоним для улучшения отображения """
    if deck.deck_class.service_name == 'Demon Hunter':
        return _('DH')
    return deck.deck_class


@register.filter(name='locrender')
def get_localized_render(card: RealCard):
    lang = to_locale(get_language())
    matches = {'en': card.image_en.url,
               'ru': card.image_ru.url}
    return matches.get(lang, card.image_en.url)
