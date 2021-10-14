from django import forms


class DeckstringForm(forms.Form):
    deckstring = forms.CharField(max_length=255, label='Deckstring')
    deckstring.widget.attrs.update({'class': 'form-deckstring', 'placeholder': 'Скопируйте сюда код колоды'})
