from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from .models import RealCard, FanCard, Author
from .forms import CreateCardForm, RealCardFilterForm, UpdateCardForm, \
    FanCardFilterForm
from core.mixins import DataMixin
import logging

logger = logging.getLogger('django')


class CreateCard(LoginRequiredMixin, DataMixin, generic.CreateView):
    """ Создание нового экземпляра фан-карты """
    form_class = CreateCardForm
    template_name = 'gallery/fancard/createcard.html'
    success_url = reverse_lazy('gallery:card_changed')

    login_url = '/accounts/signin/'

    def get_context_data(self, **kwargs):
        context = super(CreateCard, self).get_context_data(**kwargs)
        default_context = self.get_custom_context(title=_('Creation of a new card'), update=False)
        context |= default_context
        return context

    def get_initial(self):
        """ Заполнение полей начальными значениями """
        # Данные поля - скрытые
        slug = 'e-m-p-t-y'      # переопределяется в момент создания карты в соотв. с ее названием
        author = self.request.user.author
        state = True if self.request.user.has_perm('gallery.change_fancard') else False
        return {'slug': slug, 'author': author, 'state': state}


class UpdateCard(LoginRequiredMixin, UserPassesTestMixin, DataMixin, generic.UpdateView):
    """ Редактирование фан-карты """
    model = FanCard
    form_class = UpdateCardForm
    slug_url_kwarg = 'card_slug'
    template_name = 'gallery/fancard/createcard.html'

    login_url = '/accounts/signin/'

    def get_context_data(self, **kwargs):
        context = super(UpdateCard, self).get_context_data(**kwargs)
        title = _('Editing card %(card)s') % {'card': self.object.name}
        default_context = self.get_custom_context(title=title, slug=self.object.slug, update=True)
        context |= default_context
        return context

    def test_func(self):
        # Фан-карту могут изменять только пользователи с особыми полномочиями
        # и ее непосредственный создатель
        obj = self.get_object()
        return any((obj.author == self.request.user.author,
                    self.request.user.has_perm('gallery.change_fancard')))

    def form_valid(self, form):
        fan_card = form.save(commit=False)
        # Карты, созданные пользователем без ососбых полномочий, не будут отображаться на сайте
        # до тех пор, пока не будут одобрены через админку
        if not self.request.user.has_perm('gallery.change_fancard'):
            fan_card.state = False
        fan_card.save()
        form.save_m2m()
        return redirect(reverse_lazy('gallery:card_changed'))


def card_changed(request):
    """ Уведомление о создании/изменении карты и наличии премодерации на сайте """
    context = {'title': _('The card has been changed'),
               'top_menu': settings.TOP_MENU,
               'side_menu': settings.SIDE_MENU}
    return render(request,
                  template_name='gallery/fancard/card_changed.html',
                  context=context)


class DeleteCard(LoginRequiredMixin, UserPassesTestMixin, DataMixin, generic.DeleteView):
    """ Удаление фан-карты """
    model = FanCard
    slug_url_kwarg = 'card_slug'
    success_url = reverse_lazy('gallery:fancards')
    template_name = 'gallery/fancard/deletecard.html'

    login_url = '/accounts/signin/'

    def get_context_data(self, **kwargs):
        context = super(DeleteCard, self).get_context_data(**kwargs)
        title = _('Removing card %(card)s') % {'card': self.object.name}
        default_context = self.get_custom_context(title=title,
                                                  slug=self.object.slug,
                                                  name=self.object.name)
        context |= default_context
        return context

    def test_func(self):
        obj = self.get_object()
        return any((obj.author == self.request.user.author,
                    self.request.user.has_perm('gallery.delete_fancard')))


class RealCardListView(DataMixin, generic.ListView):
    """ Список существующих карт Hearthsone """
    model = RealCard
    context_object_name = 'realcards'
    template_name = 'gallery/realcard/realcard_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)

        prev_values = {'name': self.request.GET.get('name', ''),
                       'rarity': self.request.GET.get('rarity', ''),
                       'collectible': self.request.GET.get('collectible', ''),
                       'card_type': self.request.GET.get('card_type', ''),
                       'tribe': self.request.GET.get('tribe', ''),
                       'card_class': self.request.GET.get('card_class', ''),
                       'card_set': self.request.GET.get('card_set', ''),
                       'mechanic': self.request.GET.get('mechanic')}
        default_context = self.get_custom_context(title=_('Hearthstone cards'),
                                                  form=RealCardFilterForm(initial=prev_values))
        context |= default_context
        return context

    def get_queryset(self):
        """ Реализация динамического поиска по картам """
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
        object_list = self.model.objects.prefetch_related('card_set', 'tribe', 'card_class', 'mechanic')

        if name:
            object_list = object_list.search_by_name(name)
        if rarity:
            object_list = object_list.search_by_rarity(rarity)
        if collectible is not None:
            object_list = object_list.search_collectible(collectible)
        if card_type:
            object_list = object_list.search_by_type(card_type)
            if card_type == 'H' and collectible:
                object_list = object_list.exclude(card_set__service_name='Hero Skins')
        if tribe:
            object_list = object_list.search_by_tribe(tribe)
        if card_class:
            object_list = object_list.search_by_class(card_class)
        if card_set:
            object_list = object_list.search_by_set(card_set)
        if mechanic:
            object_list = object_list.search_by_mechanic(mechanic)
        return object_list


class RealCardDetailView(DataMixin, generic.DetailView):
    """ Детальная информация о существующей карте Hearthstone """
    model = RealCard
    slug_url_kwarg = 'card_slug'
    context_object_name = 'real_card'
    template_name = 'gallery/realcard/realcard_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        default_context = self.get_custom_context(title=context['object'], c_types=RealCard.CardTypes)
        context |= default_context
        return context


class FanCardListView(DataMixin, generic.ListView):
    """ Список фан-карт """
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
        context = super().get_context_data(**kwargs)
        prev_values = {'name': self.request.GET.get('name')}
        default_context = self.get_custom_context(title=_('Fan cards'),
                                                  form=FanCardFilterForm(initial=prev_values))
        context |= default_context
        return context


class FanCardDetailView(DataMixin, generic.DetailView):
    """ Детальная информация о фан-карте """
    model = FanCard
    slug_url_kwarg = 'card_slug'
    context_object_name = 'fan_card'
    template_name = 'gallery/fancard/fancard_detail.html'
    queryset = FanCard.objects.filter(state=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        default_context = self.get_custom_context(title=context['object'], c_types=FanCard.CardTypes)
        context |= default_context
        return context


class AuthorListView(DataMixin, generic.ListView):
    """ Список авторов фан-карт """
    model = Author
    template_name = 'gallery/authors/author_list.html'
    context_object_name = 'authors'

    paginate_by = 50

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        default_context = self.get_custom_context(title=_('Fan-card authors'))
        context |= default_context
        return context

    def get_queryset(self):
        return self.model.objects.active().select_related('user').prefetch_related('fancard_set')


class AuthorDetailView(DataMixin, generic.DetailView):
    """ Страница с автором и списком созданных им фан-карт """
    model = Author
    template_name = 'gallery/authors/author_detail.html'
    pk_url_kwarg = 'author_id'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        default_context = self.get_custom_context(title=self.object.user.username)
        context |= default_context
        return context

    def get_queryset(self):
        return self.model.objects.prefetch_related('fancard_set__card_class').select_related('user')
