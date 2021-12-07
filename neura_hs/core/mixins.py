from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from slugify import slugify as translit_slugify
from gallery.models import RealCard, FanCard, CardClass, Tribe
from django.conf import settings
import time


class DataMixin:
    paginate_by = 100

    def get_custom_context(self, **kwargs):
        """
        Вспомогательный метод формирования контекста шаблона по умолчанию
        :param kwargs: именованные аргументы, помещаемые в контекст из views
        :return: переменная контекста
        """
        # повторяющийся контекст (меню и т.д.)

        context = kwargs

        context['top_menu'] = settings.TOP_MENU
        context['side_menu'] = settings.SIDE_MENU

        return context


class EditCardMixin:
    """ Объединяет пользовательские валидаторы для форм создания и редактирования карт """

    def clean_name(self: forms.ModelForm):
        """ Валидатор длины названия """
        name = self.cleaned_data['name']
        max_symbols = 30
        if len(name) > max_symbols:
            msg = _('"%(name)s" is longer than %(num)s characters') % {'name': name, 'num': max_symbols}
            raise ValidationError(msg)
        return name

    def clean_card_class(self: forms.ModelForm):
        """ Валидатор, контролирующий количество выбираемых классов """

        card_classes = self.cleaned_data['card_class']
        neutral = CardClass.objects.get(service_name='Neutral')
        if neutral in card_classes:
            return [neutral]    # нейтральный класс устанавливается независимо от прочих выбранных классов
        if (num := len(card_classes)) > 3:
            msg = _('A maximum of 3 classes can be selected (selected: %(num)s)') % {'num': num}
            raise ValidationError(msg)
        return card_classes

    def clean_tribe(self: forms.ModelForm):
        """ Валидатор, запрещающий выбор расы не для существа и контролирующий кол-во рас """
        tribes = self.cleaned_data['tribe']
        alltribe = Tribe.objects.get(service_name='All')
        if alltribe in tribes:
            return [alltribe]   # раса "Всё" устанавливается независимо от прочих выбранных рас
        if tribes and self.cleaned_data['card_type'] != FanCard.CardTypes.MINION:
            raise ValidationError(_('Tribe can only be specified for minions. Ctrl + LMB - deselect the tribe.'))
        if (num := len(tribes)) > 2:
            msg = _('You can select up to 2 races (selected: %(num)s)') % {'num': num}
            raise ValidationError(msg)
        return tribes

    def clean_spell_school(self: forms.ModelForm):
        """ Валидатор, запрещающий выбор Spell School не для заклинания """
        spell_school = self.cleaned_data['spell_school']
        if spell_school and self.cleaned_data['card_type'] != FanCard.CardTypes.SPELL:
            raise ValidationError(_('The spell type can only be specified for... well, spells.'))
        return spell_school

    def clean_attack(self: forms.ModelForm):
        """ Валидатор, запрещающий установку показателя атаки не для существа/оружия """
        attack = self.cleaned_data['attack']
        if attack and self.cleaned_data['card_type'] not in [FanCard.CardTypes.MINION, FanCard.CardTypes.WEAPON]:
            raise ValidationError(_('Attack can only be specified for minion or weapon.'))
        return attack

    def clean_health(self: forms.ModelForm):
        """ Валидатор, запрещающий установку показателя здоровья не для существа """
        health = self.cleaned_data['health']
        if health and self.cleaned_data['card_type'] != FanCard.CardTypes.MINION:
            raise ValidationError(_('Only minions can have a health.'))
        return health

    def clean_durability(self: forms.ModelForm):
        """ Валидатор, запрещающий установку показателя прочности не для оружия """
        durability = self.cleaned_data['durability']
        if durability and self.cleaned_data['card_type'] != FanCard.CardTypes.WEAPON:
            raise ValidationError(_('Only weapons can have a durability.'))
        return durability

    def clean_armor(self: forms.ModelForm):
        """ Вадидатор, запрещающий установку показателя брони не для карты героя """
        armor = self.cleaned_data['armor']
        if armor and self.cleaned_data['card_type'] != FanCard.CardTypes.HERO:
            raise ValidationError(_('Only hero cards can have an armor.'))
        return armor

    def clean_slug(self: forms.ModelForm):
        """ Перезапись слага в соответствии с введенным названием """
        name = self.cleaned_data['name']
        slug = f'{translit_slugify(name)}-{int(time.time()):x}'   # унификация слага фан-карт с пом. UNIX-времени
        return slug

    class BaseMeta:
        """ Содержит общие мета-атрибуты форм создания и редактирования карт """
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'card_type': forms.Select(attrs={'class': 'form-input'}),
            'card_class': forms.SelectMultiple(attrs={'class': 'form-input'}),
            'cost': forms.NumberInput(attrs={'class': 'form-input'}),
            'attack': forms.NumberInput(attrs={'class': 'form-input'}),
            'health': forms.NumberInput(attrs={'class': 'form-input'}),
            'durability': forms.NumberInput(attrs={'class': 'form-input'}),
            'armor': forms.NumberInput(attrs={'class': 'form-input'}),
            'text': forms.Textarea(attrs={'cols': 30, 'rows': 5, 'class': 'no-resize form-input'}),
            'flavor': forms.Textarea(attrs={'cols': 30, 'rows': 6, 'class': 'no-resize form-input'}),
            'rarity': forms.Select(attrs={'class': 'form-input'}),
            'tribe': forms.SelectMultiple(attrs={'class': 'form-input'}),
            'spell_school': forms.Select(attrs={'class': 'form-input'}),
        }
