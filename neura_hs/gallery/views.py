from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.conf import settings
from .models import RealCard, FanCard, NeuraCard, CardClass, Tribe, CardSet, Author
from .forms import CreateCardForm, RealCardFilterForm, UpdateCardForm, \
    FanCardFilterForm
from utils.mixins import DataMixin
from utils.handlers import log_all_exceptions, LogAllExceptions
import logging

logger = logging.getLogger('django')


@log_all_exceptions
def index(request):
    """
    Функция отображения главной страницы сайта
    :param request: ссылка на экземпляр класса HttpRequest, содержащий информацию о запросе, сессии, куки и т.д.
    :return: экземпляр HttpResponse (страница HTML)
    """
    num_fancards = FanCard.objects.count()
    num_leg_fancards = FanCard.objects.search_by_rarity(RealCard.Rarities.LEGENDARY).count()
    num_realcards_all = RealCard.objects.count()
    collectibles = RealCard.objects.search_collectible(True)
    num_realcards_coll = collectibles.count()
    num_realcards_leg = collectibles.search_by_rarity(RealCard.Rarities.LEGENDARY).count()
    num_realcards_epic = collectibles.search_by_rarity(RealCard.Rarities.EPIC).count()
    num_realcards_rare = collectibles.search_by_rarity(RealCard.Rarities.RARE).count()
    num_realcards_common = collectibles.search_by_rarity(RealCard.Rarities.COMMON).count()
    num_realcards_bc = collectibles.search_by_mechanic(RealCard.Mechanics.BATTLECRY).count()
    num_realcards_dr = collectibles.search_by_mechanic(RealCard.Mechanics.DEATHRATTLE).count()
    num_realcards_lf = collectibles.search_by_mechanic(RealCard.Mechanics.LIFESTEAL).count()
    num_realcards_spells = collectibles.search_by_type(RealCard.CardTypes.SPELL).count()

    card_types = RealCard.CardTypes

    context = {'num_fancards': num_fancards,
               'num_leg_fancards': num_leg_fancards,
               'num_realcards_all': num_realcards_all,
               'num_realcards_coll': num_realcards_coll,
               'num_realcards_leg': num_realcards_leg,
               'num_realcards_epic': num_realcards_epic,
               'num_realcards_rare': num_realcards_rare,
               'num_realcards_common': num_realcards_common,
               'num_realcards_bc': num_realcards_bc,
               'num_realcards_dr': num_realcards_dr,
               'num_realcards_lf': num_realcards_lf,
               'num_realcards_spells': num_realcards_spells,
               'card_types': card_types,
               'top_menu': settings.TOP_MENU,
               'side_menu': settings.SIDE_MENU}

    return render(request=request,
                  template_name='gallery/index.html',
                  context=context)


class CreateCard(LoginRequiredMixin, DataMixin, generic.CreateView, LogAllExceptions):
    """ Создание нового экземпляра фан-карты """
    form_class = CreateCardForm
    template_name = 'gallery/fancard/createcard.html'
    success_url = reverse_lazy('gallery:card_changed')

    login_url = '/accounts/signin/'

    def get_context_data(self, **kwargs):
        context = super(CreateCard, self).get_context_data(**kwargs)
        default_context = self.get_custom_context(title='Создание новой карты')
        context |= default_context
        return context

    def get_initial(self):
        """ Заполнение полей начальными значениями """
        slug = 'e-m-p-t-y'
        # slug = 1/0
        author = self.request.user.author
        state = True if self.request.user.is_superuser else False
        return {'slug': slug, 'author': author, 'state': state}


class UpdateCard(LoginRequiredMixin, UserPassesTestMixin, DataMixin, generic.UpdateView, LogAllExceptions):
    """ Редактирование фан-карты """
    model = FanCard
    form_class = UpdateCardForm
    slug_url_kwarg = 'card_slug'
    template_name = 'gallery/fancard/updatecard.html'

    login_url = '/accounts/signin/'

    def get_context_data(self, **kwargs):
        context = super(UpdateCard, self).get_context_data(**kwargs)
        default_context = self.get_custom_context(title=f'Редактирование карты "{self.object.name}"',
                                                  slug=self.object.slug)
        context |= default_context
        return context

    def test_func(self):
        obj = self.get_object()
        return any((obj.author == self.request.user.author,
                    self.request.user.has_perm('gallery.change_fancard')))

    def form_valid(self, form):
        fan_card = form.save(commit=False)
        if not self.request.user.is_superuser:
            fan_card.state = False
        fan_card.save()
        return redirect(reverse_lazy('gallery:card_changed'))


@log_all_exceptions
def card_changed(request):
    context = {'title': 'Карта была изменена',
               'top_menu': settings.TOP_MENU,
               'side_menu': settings.SIDE_MENU}
    return render(request,
                  template_name='gallery/fancard/card_changed.html',
                  context=context)


class DeleteCard(LoginRequiredMixin, UserPassesTestMixin, DataMixin, generic.DeleteView, LogAllExceptions):
    """ Удаление фан-карты """
    model = FanCard
    slug_url_kwarg = 'card_slug'
    success_url = reverse_lazy('gallery:fancards')
    template_name = 'gallery/fancard/deletecard.html'

    login_url = '/accounts/signin/'

    def get_context_data(self, **kwargs):
        context = super(DeleteCard, self).get_context_data(**kwargs)
        default_context = self.get_custom_context(title=f'Удаление карты "{self.object.name}"',
                                                  slug=self.object.slug,
                                                  name=self.object.name)
        context |= default_context
        return context

    def test_func(self):
        obj = self.get_object()
        return any((obj.author == self.request.user.author,
                    self.request.user.has_perm('gallery.delete_fancard')))


class RealCardListView(DataMixin, generic.ListView, LogAllExceptions):
    """ Обобщенный класс отображения списка реальных карт Hearthsone """
    model = RealCard
    context_object_name = 'realcards'
    template_name = 'gallery/realcard/realcard_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        # переменная form, ссылающаяся на форму фильтрации, будет доступна в шаблоне
        # форма по умолчанию заполняется данными из словаря GET объекта HTTPRequest (форма сохранит предыдущие значения)
        prev_values = {'name': self.request.GET.get('name', ''),
                       'rarity': self.request.GET.get('rarity', ''),
                       'collectible': self.request.GET.get('collectible', ''),
                       'card_type': self.request.GET.get('card_type', ''),
                       'tribe': self.request.GET.get('tribe', ''),
                       'card_class': self.request.GET.get('card_class', ''),
                       'card_set': self.request.GET.get('card_set', ''),
                       'mechanic': self.request.GET.get('mechanic')}
        default_context = self.get_custom_context(title='Карты Hearthstone',
                                                  form=RealCardFilterForm(initial=prev_values))
        context |= default_context
        return context

    def get_queryset(self):
        """ Метод переопределен для возможности динамического поиска по картам """
        name = self.request.GET.get('name')
        rarity = self.request.GET.get('rarity')
        collectible_raw = self.request.GET.get('collectible', 'unknown')
        collectible = {'unknown': None,
                       'true': True,
                       'false': False}.get(collectible_raw)
        card_type = self.request.GET.get('card_type')
        tribe = self.request.GET.get('tribe')
        card_class = self.request.GET.get('card_class')
        card_set = self.request.GET.get('card_set')
        mechanic = self.request.GET.get('mechanic')

        # Оптимизация: вместо множества SQL-запросов - один сложный
        object_list = self.model.objects.prefetch_related('card_set', 'tribe', 'card_class')

        if name:
            object_list = object_list.search_by_name(name)
        if rarity:
            object_list = object_list.search_by_rarity(rarity)
        if collectible is not None:
            object_list = object_list.search_collectible(collectible)
        if card_type:
            object_list = object_list.search_by_type(card_type)
        if tribe:
            object_list = object_list.search_by_tribe(tribe)
        if card_class:
            object_list = object_list.search_by_class(card_class)
        if card_set:
            object_list = object_list.search_by_set(card_set)
        if mechanic:
            object_list = object_list.search_by_mechanic(mechanic)
        return object_list


class RealCardDetailView(DataMixin, generic.DetailView, LogAllExceptions):
    """ Обобщенный класс отображения детальной информации о карте Hearthstone """
    model = RealCard
    slug_url_kwarg = 'card_slug'
    context_object_name = 'real_card'
    template_name = 'gallery/realcard/realcard_detail.html'

    def get_context_data(self, **kwargs):
        """ Переопределение метода для передачи шаблону дополнительных переменных """
        context = super().get_context_data(**kwargs)
        default_context = self.get_custom_context(title=context['object'], c_types=RealCard.CardTypes)
        context |= default_context
        return context


class FanCardListView(DataMixin, generic.ListView, LogAllExceptions):
    """ Обобщенный класс отображения списка фан-карт """
    model = FanCard
    context_object_name = 'fancards'
    template_name = 'gallery/fancard/fancard_list.html'

    def get_queryset(self):
        """ Переопределение метода получения списка всех записей """

        name = self.request.GET.get('name')

        object_list = self.model.objects.filter(state=True)
        # Оптимизация: вместо множества SQL-запросов - один сложный
        object_list = object_list.select_related('author__user').prefetch_related('card_class').all()

        if name:
            object_list = object_list.search_by_name(name)

        return object_list

    def get_context_data(self, **kwargs):
        """ Переопределение метода для передачи шаблону дополнительных переменных """
        context = super().get_context_data(**kwargs)
        prev_values = {'name': self.request.GET.get('name')}
        default_context = self.get_custom_context(title='Фан-карты',
                                                  form=FanCardFilterForm(initial=prev_values))
        context |= default_context
        return context


class FanCardDetailView(DataMixin, generic.DetailView, LogAllExceptions):
    """ Обобщенный класс отображения детальной информации о карте """
    model = FanCard
    slug_url_kwarg = 'card_slug'
    context_object_name = 'fan_card'
    template_name = 'gallery/fancard/fancard_detail.html'
    queryset = FanCard.objects.filter(state=True)

    def get_context_data(self, **kwargs):
        """ Переопределение метода для передачи шаблону дополнительных переменных """
        context = super().get_context_data(**kwargs)
        default_context = self.get_custom_context(title=context['object'], c_types=FanCard.CardTypes)
        context |= default_context
        return context


class NeuraCardListView(DataMixin, generic.ListView, LogAllExceptions):
    """ Обобщенный класс отображения списка сгенерированных карт """
    model = NeuraCard
    context_object_name = 'neuracards'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        default_context = self.get_custom_context(title='Нейрокарты')
        context |= default_context
        return context


class AuthorListView(DataMixin, generic.ListView, LogAllExceptions):
    """  """
    model = Author
    template_name = 'gallery/authors/author_list.html'
    context_object_name = 'authors'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        default_context = self.get_custom_context(title='Авторы фан-карт')
        context |= default_context
        return context

    def get_queryset(self):
        return self.model.objects.select_related('user').prefetch_related('fancard_set')


class AuthorDetailView(DataMixin, generic.DetailView, LogAllExceptions):
    """  """
    model = Author
    template_name = 'gallery/authors/author_detail.html'
    pk_url_kwarg = 'author_id'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        default_context = self.get_custom_context(title='Авторы фан-карт')
        context |= default_context
        return context

    def get_queryset(self):
        return self.model.objects.prefetch_related('fancard_set__card_class').select_related('user')
