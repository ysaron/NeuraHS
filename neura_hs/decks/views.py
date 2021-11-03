from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from utils.mixins import DataMixin
from utils.handlers import log_all_exceptions, LogAllExceptions
import logging
from .models import Format, Deck, Inclusion
from .forms import DeckstringForm, DeckSaveForm, DeckFilterForm
from .decrypt import DecodeError


def create_deck(request: HttpRequest):
    """ Форма для кода колоды + ее отображение """

    deck, deckstring_form, deck_save_form = None, None, None
    title = 'Расшифровка колоды'

    if request.method == 'POST':
        if 'deckstring' in request.POST:        # код колоды отправлен с формы DeckstringForm
            deckstring_form = DeckstringForm(request.POST)
            if deckstring_form.is_valid():
                try:
                    deckstring = deckstring_form.cleaned_data['deckstring']
                    deck = Deck.create_from_deckstring(deckstring)
                    deck_name_init = f'{deck.deck_class}-{deck.pk}'
                    deck_save_form = DeckSaveForm(initial={'string_to_save': deckstring,
                                                           'deck_name': deck_name_init})
                    title = deck
                except DecodeError as de:
                    deckstring_form.add_error(None, f'Ошибка: {de}')
        if 'deck_name' in request.POST:         # название колоды отправлено с формы DeckSaveForm
            deck = Deck.create_from_deckstring(request.POST['string_to_save'], named=True)
            deck.author = request.user.author
            deck.name = request.POST['deck_name']
            deck.save()
            return redirect(deck)
    else:
        deckstring_form = DeckstringForm()

    context = {'title': title,
               'deckstring_form': deckstring_form,
               'deck_save_form': deck_save_form,
               'deck': deck}
    context |= {'top_menu': settings.TOP_MENU,
                'side_menu': settings.SIDE_MENU}

    return render(request, template_name='decks/deck_detail.html', context=context)


class NamelessDecksListView(DataMixin, generic.ListView):
    """  """
    model = Deck
    context_object_name = 'decks'
    template_name = 'decks/deck_list.html'
    paginate_by = 5

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        search_initial_values = {'deck_class': self.request.GET.get('deck_class', ''),
                                 'deck_format': self.request.GET.get('deck_format', '')}

        default_context = self.get_custom_context(title='Деки',
                                                  form=DeckFilterForm(initial=search_initial_values))
        context |= default_context
        return context

    def get_queryset(self):
        deck_class = self.request.GET.get('deck_class')
        deck_format = self.request.GET.get('deck_format')

        object_list = self.model.nameless.all()
        if deck_class:
            object_list = object_list.filter(deck_class=deck_class)
        if deck_format:
            object_list = object_list.filter(deck_format=deck_format)

        return object_list


class UserDecksListView(DataMixin, generic.ListView):
    """  """

    model = Deck
    context_object_name = 'decks'
    template_name = 'decks/deck_list.html'
    paginate_by = 5

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        search_initial_values = {'deck_class': self.request.GET.get('deck_class', ''),
                                 'deck_format': self.request.GET.get('deck_format', '')}

        default_context = self.get_custom_context(title='Деки',
                                                  form=DeckFilterForm(initial=search_initial_values))
        context |= default_context
        return context

    def get_queryset(self):

        deck_class = self.request.GET.get('deck_class')
        deck_format = self.request.GET.get('deck_format')

        object_list = self.model.named.filter(author=self.request.user.author)
        if deck_class:
            object_list = object_list.filter(deck_class=deck_class)
        if deck_format:
            object_list = object_list.filter(deck_format=deck_format)

        return object_list


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


def deck_view(request, deck_id):
    """  """

    deck = Deck.objects.get(id=deck_id)
    deck_name_init = '' if deck.is_named else f'{deck.deck_class}-{deck.pk}'
    deck_save_form = DeckSaveForm(initial={'string_to_save': deck.string, 'deck_name': deck_name_init})

    # --- Ограничение доступа к именованным колодам ------------------------
    if deck.is_named:
        if not request.user.is_authenticated or deck.author != request.user.author:
            raise PermissionDenied()

    if request.method == 'POST':
        if deck.is_named:
            # доступно переименование и удаление колоды
            if new_name := request.POST['deck_name'].strip():
                deck.name = new_name
                deck.save()
        else:
            # доступно сохранение колоды (т.е. создание именованного экземпляра той же колоды)
            deck_to_save = Deck.create_from_deckstring(request.POST['string_to_save'], named=True)
            deck_to_save.author = request.user.author
            deck_to_save.name = request.POST['deck_name']
            deck_to_save.save()
            return redirect(deck_to_save)

    context = {'title': deck,
               'deck': deck,
               'deck_save_form': deck_save_form}
    context |= {'top_menu': settings.TOP_MENU,
                'side_menu': settings.SIDE_MENU}

    return render(request, template_name='decks/deck_detail.html', context=context)


class DeckDelete(SuccessMessageMixin, generic.DeleteView):
    """  """

    model = Deck
    pk_url_kwarg = 'deck_id'
    success_url = reverse_lazy('decks:user_decks')
    success_message = 'Колода %(name)s была удалена'

    def get_queryset(self):
        return self.model.named.all()

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, self.success_message % obj.__dict__)
        return super(DeckDelete, self).delete(request, *args, **kwargs)
