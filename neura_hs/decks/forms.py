from django import forms


class DeckstringForm(forms.Form):
    deckstring = forms.CharField(max_length=255, label='Deckstring')
    deckstring.widget.attrs.update({'class': 'form-deckstring', 'placeholder': 'Скопируйте сюда код колоды'})


class DeckSaveForm(forms.Form):
    deck_name = forms.CharField(max_length=255, label='Name', required=False)
    string_to_save = forms.CharField(max_length=255)

    deck_name.widget.attrs.update({'class': 'form-deck-name', 'placeholder': 'Введите название для колоды'})
    string_to_save.widget.attrs.update({'style': 'display: none;'})
