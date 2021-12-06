from django import forms
from django.utils.translation import gettext_lazy as _
from .models import RealCard, FanCard, CardClass, Tribe, CardSet
from core.mixins import EditCardMixin


class CreateCardForm(EditCardMixin, forms.ModelForm):

    class Meta(EditCardMixin.BaseMeta):
        model = FanCard
        fields = ['name', 'card_type', 'card_class', 'cost', 'attack', 'health', 'durability', 'armor',
                  'text', 'flavor', 'rarity', 'tribe', 'spell_school',
                  'slug', 'author', 'state',        # скрытые поля
                  'spell_school']


class UpdateCardForm(EditCardMixin, forms.ModelForm):

    class Meta(EditCardMixin.BaseMeta):
        model = FanCard
        fields = ['name', 'card_type', 'card_class', 'cost', 'attack', 'health', 'durability', 'armor',
                  'text', 'flavor', 'rarity', 'tribe', 'spell_school']


class RealCardFilterForm(forms.Form):
    """ Форма фильтрации и поиска карт Hearthstone """
    name = forms.CharField(required=False, label=_('Name'))

    RARITIES = RealCard.Rarities.choices
    rarity = forms.ChoiceField(choices=RARITIES, required=False, label=_('Rarity'))

    collectible = forms.NullBooleanField(required=False, label=_('Collectible'))

    MECHANICS = RealCard.Mechanics.choices
    mechanic = forms.ChoiceField(choices=MECHANICS, required=False, label=_('Mechanics'))

    CARD_TYPES = RealCard.CardTypes.choices
    card_type = forms.ChoiceField(choices=CARD_TYPES, required=False, label=_('Type'))

    TRIBES = Tribe.objects.all()
    tribe = forms.ModelChoiceField(queryset=TRIBES, required=False, label=_('Tribe'))

    CARD_CLASSES = CardClass.objects.all()
    card_class = forms.ModelChoiceField(queryset=CARD_CLASSES, required=False, label=_('Class'))

    CARD_SETS = CardSet.objects.all()
    card_set = forms.ModelChoiceField(queryset=CARD_SETS, required=False, label=_('Set'))

    # update() в данном случае лаконичнее, чем |
    name.widget.attrs.update({'class': 'form-input', 'placeholder': _('Enter card name')})
    rarity.widget.attrs.update({'class': 'form-input'})
    collectible.widget.attrs.update({'class': 'form-input'})
    card_type.widget.attrs.update({'class': 'form-input'})
    tribe.widget.attrs.update({'class': 'form-input'})
    card_class.widget.attrs.update({'class': 'form-input'})
    card_set.widget.attrs.update({'class': 'form-input'})
    mechanic.widget.attrs.update({'class': 'form-input'})


class FanCardFilterForm(forms.Form):
    """ Форма фильтрации и поиска фан-карт """
    name = forms.CharField(required=False, label=_('Name'))

    name.widget.attrs.update({'class': 'form-input', 'placeholder': _('Enter card name')})
