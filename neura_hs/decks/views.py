from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.conf import settings
from utils.mixins import DataMixin
from utils.handlers import log_all_exceptions, LogAllExceptions
import logging
from .models import Format, Deck, Inclusion
from .forms import DeckstringForm
from .decrypt import DecodeError


def main(request: HttpRequest):
    """ Форма для кода колоды + ее отображение """

    deck = None
    title = 'Расшифровка колоды'

    if request.method == 'POST':    # данные с формы получены
        form = DeckstringForm(request.POST)     # наполняем форму принятыми значениями из request.POST
        if form.is_valid():
            try:
                deck = Deck.create_from_deckstring(form.cleaned_data["deckstring"])
                title = deck
            except DecodeError as de:
                form.add_error(None, f'Ошибка: {de}')
            except Exception as e:
                print(f'--- {e.__class__.__name__}: {e} ---')
                raise e
    else:
        form = DeckstringForm()

    context = {'title': title, 'form': form, 'deck': deck}
    context |= {'top_menu': settings.TOP_MENU,
                'side_menu': settings.SIDE_MENU}

    return render(request, template_name='decks/index.html', context=context)
