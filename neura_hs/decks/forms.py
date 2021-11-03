from django import forms
from gallery.models import CardClass
from .models import Deck, Format


class DeckstringForm(forms.Form):
    deckstring = forms.CharField(max_length=255, label='Deckstring')
    deckstring.widget.attrs.update({'class': 'form-deckstring', 'placeholder': 'Скопируйте сюда код колоды'})


class DeckSaveForm(forms.Form):
    deck_name = forms.CharField(max_length=255, label='Name', required=False)
    string_to_save = forms.CharField(max_length=255)

    deck_name.widget.attrs.update({'class': 'form-deck-name', 'placeholder': 'Введите название для колоды'})
    string_to_save.widget.attrs.update({'style': 'display: none;', 'id': 'deckstringData'})


class DeckFilterForm(forms.Form):
    CARD_CLASSES = CardClass.objects.all()
    deck_class = forms.ModelChoiceField(queryset=CARD_CLASSES, required=False, label='Класс')

    FORMATS = Format.objects.all()
    deck_format = forms.ModelChoiceField(queryset=FORMATS, required=False, label='Формат')

    deck_class.widget.attrs.update({'class': 'form-select form-select-sm'})
    deck_format.widget.attrs.update({'class': 'form-select form-select-sm'})
