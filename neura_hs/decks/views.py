from django.http import HttpRequest, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import transaction
from utils.mixins import DataMixin
from utils.handlers import log_all_exceptions, LogAllExceptions
import logging
from random import choice
from .models import Format, Deck, Inclusion
from .forms import DeckstringForm, DeckSaveForm, DeckFilterForm
from .decrypt import get_clean_deckstring
from .exceptions import DecodeError, UnsupportedCards


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
                    deckstring = get_clean_deckstring(deckstring)
                    with transaction.atomic():
                        deck = Deck.create_from_deckstring(deckstring)
                        deck_name_init = f'{deck.deck_class}-{deck.pk}'
                        deck_save_form = DeckSaveForm(initial={'string_to_save': deckstring,
                                                               'deck_name': deck_name_init})
                        title = deck
                except DecodeError as de:
                    deckstring_form.add_error(None, f'Ошибка: {de}')
                except UnsupportedCards as u:
                    deckstring_form.add_error(None, f'{u}. База данных будет обновлена в скором времени.')
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


def get_random_deckstring(request: HttpRequest):
    """ AJAX-view для получения случайного кода колоды из базы """
    if request.GET.get('deckstring') == 'random' and request.is_ajax():
        deck = choice(Deck.nameless.all())
        response = {'deckstring': deck.string}
        return JsonResponse(response)

    return redirect(reverse_lazy('decks:index'))


class NamelessDecksListView(DataMixin, generic.ListView):
    """  """
    model = Deck
    context_object_name = 'decks'
    template_name = 'decks/deck_list.html'
    paginate_by = 6

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


class UserDecksListView(LoginRequiredMixin, DataMixin, generic.ListView):
    """  """

    model = Deck
    context_object_name = 'decks'
    template_name = 'decks/deck_list.html'
    paginate_by = 6
    login_url = '/accounts/signin/'

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

