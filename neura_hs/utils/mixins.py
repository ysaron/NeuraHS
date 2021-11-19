from django import forms
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
        # Сюда можно выносить повторяющийся контекст (меню и т.д.)

        context = kwargs

        context['top_menu'] = settings.TOP_MENU
        context['side_menu'] = settings.SIDE_MENU

        return context


class EditCardMixin:
    """ Объединяет пользовательские валидаторы для форм создания и редактирования карт """

    def clean_name(self: forms.ModelForm):
        """ Пользовательский валидатор. Обязательно имеет форму "clean_<имя_поля>" """
        name = self.cleaned_data['name']
        max_symbols = 30
        if len(name) > max_symbols:
            raise ValidationError(f'Длина имени "{name}" превышает {max_symbols} символов.')
        return name

    def clean_card_class(self: forms.ModelForm):
        """ Валидатор, контролирующий количество выбираемых классов """

        card_classes = self.cleaned_data['card_class']
        neutral = CardClass.objects.get(service_name='Neutral')
        if neutral in card_classes:
            return [neutral]    # нейтральный класс устанавливается независимо от прочих выбранных классов
        if (num := len(card_classes)) > 3:
            raise ValidationError(f'Можно выбрать не более 3 классов (выбрано: {num})')
        return card_classes

    def clean_tribe(self: forms.ModelForm):
        """ Валидатор, запрещающий выбор расы не для существа и контролирующий кол-во рас """
        tribes = self.cleaned_data['tribe']
        alltribe = Tribe.objects.get(service_name='All')
        if alltribe in tribes:
            return [alltribe]   # раса "Всё" устанавливается независимо от прочих выбранных рас
        if tribes and self.cleaned_data['card_type'] != FanCard.CardTypes.MINION:
            raise ValidationError('Расу можно указывать только для существ. Ctrl + ЛКМ - отменить выбор расы.')
        if (num := len(tribes)) > 2:
            raise ValidationError(f'Можно выбрать не более 2 рас (выбрано: {num})')
        return tribes

    def clean_spell_school(self: forms.ModelForm):
        """ Валидатор, запрещающий выбор Spell School не для заклинания """
        spell_school = self.cleaned_data['spell_school']
        if spell_school and self.cleaned_data['card_type'] != FanCard.CardTypes.SPELL:
            raise ValidationError('Тип заклинания можно указать только у... ну да, заклинания.')
        return spell_school

    def clean_attack(self: forms.ModelForm):
        """ Валидатор, запрещающий установку показателя атаки не для существа/оружия """
        attack = self.cleaned_data['attack']
        if attack and self.cleaned_data['card_type'] not in [FanCard.CardTypes.MINION, FanCard.CardTypes.WEAPON]:
            raise ValidationError('Атака может быть указана только для существа и оружия.')
        return attack

    def clean_health(self: forms.ModelForm):
        """ Валидатор, запрещающий установку показателя здоровья не для существа """
        health = self.cleaned_data['health']
        if health and self.cleaned_data['card_type'] != FanCard.CardTypes.MINION:
            raise ValidationError('Только существо может иметь показатель здоровья.')
        return health

    def clean_durability(self: forms.ModelForm):
        """ Валидатор, запрещающий установку показателя прочности не для оружия """
        durability = self.cleaned_data['durability']
        if durability and self.cleaned_data['card_type'] != FanCard.CardTypes.WEAPON:
            raise ValidationError('Только оружие может иметь показатель прочности.')
        return durability

    def clean_armor(self: forms.ModelForm):
        """ Вадидатор, запрещающий установку показателя брони не для карты героя """
        armor = self.cleaned_data['armor']
        if armor and self.cleaned_data['card_type'] != FanCard.CardTypes.HERO:
            raise ValidationError('Только карта героя может иметь показатель брони.')
        return armor

    def clean_slug(self: forms.ModelForm):
        """ Перезапись слага в соответствии с введенным названием """
        name = self.cleaned_data['name']
        slug = f'{translit_slugify(name)}-{int(time.time()):x}'   # унификация слага фан-карт с пом. UNIX-времени
        return slug

    class BaseMeta:
        """ Содержит общие мета-атрибуты форм создания и редактирования карт """
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'card_type': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'card_class': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control'}),
            'attack': forms.NumberInput(attrs={'class': 'form-control'}),
            'health': forms.NumberInput(attrs={'class': 'form-control'}),
            'durability': forms.NumberInput(attrs={'class': 'form-control'}),
            'armor': forms.NumberInput(attrs={'class': 'form-control'}),
            'text': forms.Textarea(attrs={'cols': 30, 'rows': 5, 'class': 'no-resize form-control'}),
            'flavor': forms.Textarea(attrs={'cols': 30, 'rows': 6, 'class': 'no-resize form-control'}),
            'rarity': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'tribe': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'spell_school': forms.Select(attrs={'class': 'form-select form-select-sm'})
        }

