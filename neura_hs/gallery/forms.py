from django import forms
from .models import RealCard, FanCard, CardClass, Tribe, CardSet, User
from utils.mixins import EditCardMixin


class CreateCardForm(EditCardMixin, forms.ModelForm):

    # для установки свойств отдельных полей
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['tribe'].help_text = 'Раса существа'

    class Meta(EditCardMixin.BaseMeta):
        model = FanCard
        fields = ['name', 'card_type', 'card_class', 'cost', 'attack', 'health', 'durability', 'armor',
                  'text', 'flavor', 'rarity', 'tribe', 'spell_school',
                  'slug', 'author', 'state']     # последняя строка - скрытые поля


class UpdateCardForm(EditCardMixin, forms.ModelForm):

    class Meta(EditCardMixin.BaseMeta):
        model = FanCard
        fields = ['name', 'card_type', 'card_class', 'cost', 'attack', 'health', 'durability', 'armor',
                  'text', 'flavor', 'rarity', 'tribe', 'spell_school']


class RealCardFilterForm(forms.Form):
    """ Форма фильтрации и поиска карт Hearthstone """
    name = forms.CharField(required=False, label='Название')

    RARITIES = RealCard.Rarities.choices
    rarity = forms.ChoiceField(choices=RARITIES, required=False, label='Редкость')

    collectible = forms.NullBooleanField(required=False, label='Коллекционная')

    MECHANICS = RealCard.Mechanics.choices
    mechanic = forms.ChoiceField(choices=MECHANICS, required=False, label='Механика')

    CARD_TYPES = RealCard.CardTypes.choices
    card_type = forms.ChoiceField(choices=CARD_TYPES, required=False, label='Тип')

    TRIBES = Tribe.objects.all()
    tribe = forms.ModelChoiceField(queryset=TRIBES, required=False, label='Раса существа')

    CARD_CLASSES = CardClass.objects.all()
    card_class = forms.ModelChoiceField(queryset=CARD_CLASSES, required=False, label='Класс')

    CARD_SETS = CardSet.objects.all()
    card_set = forms.ModelChoiceField(queryset=CARD_SETS, required=False, label='Набор')

    # update() в данном случае лаконичнее, чем |
    name.widget.attrs.update({'class': 'form-control form-control-sm', 'placeholder': 'Введите название карты'})
    rarity.widget.attrs.update({'class': 'form-select form-select-sm', 'placeholder': 'Выберите редкость'})
    collectible.widget.attrs.update({'class': 'form-select form-select-sm', 'placeholder': 'Коллекционная ли карта'})
    card_type.widget.attrs.update({'class': 'form-select form-select-sm', 'placeholder': 'Выберите тип карты'})
    tribe.widget.attrs.update({'class': 'form-select form-select-sm', 'placeholder': 'Выберите расу существа'})
    card_class.widget.attrs.update({'class': 'form-select form-select-sm', 'placeholder': 'Выберите класс карты'})
    card_set.widget.attrs.update({'class': 'form-select form-select-sm', 'placeholder': 'Выберите набор'})
    mechanic.widget.attrs.update({'class': 'form-select form-select-sm', 'placeholder': 'Выберите набор'})


class FanCardFilterForm(forms.Form):
    """ Форма фильтрации и поиска фан-карт """
    name = forms.CharField(required=False, label='Название')

    name.widget.attrs.update({'class': 'form-control', 'placeholder': 'Введите название карты'})
