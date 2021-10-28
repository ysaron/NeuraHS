from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.conf import settings
from utils.mixins import DataMixin
from utils.handlers import log_all_exceptions, LogAllExceptions
import logging
from .models import Format, Deck, Inclusion
from .forms import DeckstringForm, DeckSaveForm
from .decrypt import DecodeError


def main(request: HttpRequest):
    """ Форма для кода колоды + ее отображение """

    deck, deckstring_form, deck_save_form = None, None, None
    title = 'Расшифровка колоды'

    if request.method == 'POST':
        if 'deckstring' in request.POST:        # код колоды отправлен с формы DeckstringForm
            deckstring_form = DeckstringForm(request.POST)
            if deckstring_form.is_valid():
                try:
                    deckstring = deckstring_form.cleaned_data['deckstring']
                    deck_save_form = DeckSaveForm(initial={'string_to_save': deckstring})
                    deck = Deck.create_from_deckstring(deckstring)
                    title = deck
                except DecodeError as de:
                    deckstring_form.add_error(None, f'Ошибка: {de}')
        if 'deck_name' in request.POST:         # название колоды отправлено с формы DeckSaveForm
            deck = Deck.create_from_deckstring(request.POST['string_to_save'], named=True)
            deck.author = request.user.author
            deck.name = request.POST['deck_name']
            deck.save()
            return redirect(reverse_lazy('decks:index'))
    else:
        deckstring_form = DeckstringForm()

    context = {'title': title,
               'deckstring_form': deckstring_form,
               'deck_save_form': deck_save_form,
               'deck': deck}
    context |= {'top_menu': settings.TOP_MENU,
                'side_menu': settings.SIDE_MENU}

    return render(request, template_name='decks/index.html', context=context)


class DeckListView(DataMixin, generic.ListView):
    """  """
    model = Deck
    context_object_name = 'decks'
    template_name = 'decks/deck_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        default_context = self.get_custom_context(title='Деки')
        context |= default_context
        return context


class NamelessDeckDetailView(DataMixin, generic.DetailView):
    """ Просмотр безымянной колоды """
    model = Deck
    template_name = 'decks/deck_detail.html'
    pk_url_kwarg = 'deck_id'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        default_context = self.get_custom_context(title=context['object'])
        context |= default_context
        return context



