from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls.base import reverse_lazy
from gallery.models import RealCard, Author, CardClass, CardSet
from core.exceptions import UnsupportedCards
from core.services.deck_codes import parse_deckstring


class IncluSionManager(models.QuerySet):

    def nameless(self):
        return self.filter(deck__name='')

    def named(self):
        return self.exclude(deck__name='')


class NamelessDeckManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(name='').prefetch_related('deck_class', 'deck_format')


class NamedDeckManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().exclude(name='').prefetch_related('deck_class', 'deck_format')


class Format(models.Model):
    """ Формат обычного режима игры Hearthstone """

    name = models.CharField(max_length=255, default=_('Unknown'), verbose_name=_('Name'))
    numerical_designation = models.PositiveSmallIntegerField(verbose_name=_('Format code'), default=0)
    available_sets = models.ManyToManyField(CardSet, blank=True, verbose_name=_('Available sets'),
                                            help_text=_('Card sets that can be used in this format'))

    class Meta:
        verbose_name = _('Format')
        verbose_name_plural = _('Formats')

    def __str__(self):
        return self.name


class Deck(models.Model):
    """ Колода Hearthstone """

    name = models.CharField(max_length=255, default='', blank=True, verbose_name=_('Name'),
                            help_text=_('User-definable name'))
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, related_name='decks', null=True, blank=True,
                               verbose_name=_('Author'))
    string = models.TextField(max_length=1500, verbose_name=_('Deck code'),
                              help_text=_('The string used to identify the cards that make up the deck.'))
    cards = models.ManyToManyField(RealCard, through='Inclusion',
                                   verbose_name=_('Cards'), help_text=_('The cards that make up the deck.'))
    deck_class = models.ForeignKey(CardClass, on_delete=models.CASCADE, related_name='decks', verbose_name=_('Class'),
                                   help_text=_('The class for which the deck is built.'))
    deck_format = models.ForeignKey(Format, on_delete=models.CASCADE,
                                    related_name='decks', verbose_name=_('Formats'),
                                    help_text=_('The format for which the deck is intended.'))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('Time of creation.'))

    nameless = NamelessDeckManager()
    objects = models.Manager()
    named = NamedDeckManager()

    class Meta:
        verbose_name = _('Deck')
        verbose_name_plural = _('Decks')
        ordering = ['-created']

    def __str__(self):
        kinda_name = self.name if self.name else f'id_{self.pk}'
        return f'{kinda_name} ({self.deck_format}, {self.deck_class})'

    @classmethod
    def create_from_deckstring(cls, deckstring: str, *, named: bool = False):
        """ Создает экземпляр колоды из кода, сохраняет и возвращает его """

        # если точно такая же колода уже есть в БД - она же и возвращается вместо создания нового экземпляра
        nameless_deck = Deck.nameless.filter(string=deckstring)
        if not named and nameless_deck.exists():
            return nameless_deck.first()

        instance = cls()
        cards, heroes, format_ = parse_deckstring(deckstring)
        instance.deck_class = RealCard.objects.get(dbf_id=heroes[0]).card_class.all().first()
        instance.deck_format = Format.objects.get(numerical_designation=format_)
        instance.string = deckstring
        instance.save()
        for dbf_id, number in cards:
            try:
                card = RealCard.includibles.get(dbf_id=dbf_id)
            except RealCard.DoesNotExist:
                msg = _('No card data (id %(id)s)') % {'id': dbf_id}
                raise UnsupportedCards(msg)
            ci = Inclusion(deck=instance, card=card, number=number)
            ci.save()
            instance.cards.add(card)

        return instance

    @property
    def is_named(self):
        """ Возвращает True, если колода была сохранена пользователем """
        return self.name != '' and self.author is not None

    @property
    def included_cards(self):
        """ Queryset 'cards', дополненный данными о количестве экземпляров в колоде """

        decklist = self.cards.all().prefetch_related('card_class', 'tribe').select_related('card_set')\
            .annotate(number=models.F('inclusions__number'))
        return decklist.order_by('cost', 'name')

    def get_deckstring_form(self):
        """ Возвращает форму, используемую для копирования кода колоды """
        from .forms import DeckStringCopyForm   # импорт здесь во избежание перекрестного импорта
        return DeckStringCopyForm(initial={'deckstring': self.string})

    def get_absolute_url(self):
        return reverse_lazy('decks:deck-detail', kwargs={'deck_id': self.pk})


class Inclusion(models.Model):
    """ Параметры вхождения карты в колоду (Intermediate Model) """
    card = models.ForeignKey(RealCard, on_delete=models.CASCADE, related_name='inclusions')
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name='inclusions')
    number = models.PositiveSmallIntegerField(verbose_name=_('Amount'),
                                              help_text=_('The number of card inclusions in the deck.'))

    objects = IncluSionManager.as_manager()
