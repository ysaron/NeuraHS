from django.db import models
from django.utils.translation import gettext_lazy as _
from gallery.models import RealCard, Author, CardClass, CardSet
from .decrypt import parse_deckstring


class Format(models.Model):
    """ Формат обычного режима игры Hearthstone """

    class Formats(models.TextChoices):
        UNKNOWN = '0', _('---------')
        WILD = '1', _('Wild')
        STANDARD = '2', _('Standard')
        CLASSIC = '3', _('Classic')

    name = models.CharField(max_length=2, choices=Formats.choices, verbose_name='Название')
    available_sets = models.ManyToManyField(CardSet, blank=True, verbose_name='Доступные аддоны',
                                            help_text='Наборы карт, которые можно использовать в данном формате')

    class Meta:
        verbose_name = 'Формат'
        verbose_name_plural = 'Форматы'

    def __str__(self):
        return self.name


class Deck(models.Model):
    """ Колода Hearthstone """

    name = models.CharField(max_length=255, default='', verbose_name='Название',
                            help_text='Название, устанавливаемое пользователем')
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, related_name='decks', null=True, blank=True,
                               verbose_name='Автор', help_text='')
    string = models.CharField(max_length=255, verbose_name='Код колоды',
                              help_text='Код, используемый для определения карт, составляющих колоду')
    cards = models.ManyToManyField(RealCard, through='Inclusion',
                                   verbose_name='Карты', help_text='Карты, составляющие колоду')
    deck_class = models.ForeignKey(CardClass, on_delete=models.CASCADE, related_name='decks', verbose_name='Класс',
                                   help_text='Класс, для которого составлена колода')
    deck_format = models.ForeignKey(Format, default='', on_delete=models.SET_DEFAULT, related_name='decks',
                                    verbose_name='Формат', help_text='Формат, для которого предназначена колода')
    created = models.DateField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Колода'
        verbose_name_plural = 'Колоды'

    def __str__(self):
        return f'[{Format.Formats(str(self.deck_format)).label}] [{self.deck_class}] {self.name}'

    @classmethod
    def create_from_deckstring(cls, deckstring: str):
        """ Создает экземпляр колоды из кода, сохраняет и возвращает его """

        # если точно такая же колода уже есть в БД - она же и возвращается вместо создания нового экземпляра
        nameless_deck = Deck.objects.filter(string=deckstring)
        if nameless_deck.exists():
            return nameless_deck.first()

        instance = cls()
        cards, heroes, format_ = parse_deckstring(deckstring)
        instance.deck_class = RealCard.objects.get(dbf_id=heroes[0]).card_class.all()[0]
        instance.deck_format = Format.objects.get(name=str(format_))
        instance.string = deckstring
        instance.save()
        for dbf_id, number in cards:
            card = RealCard.includibles.get(dbf_id=dbf_id)
            ci = Inclusion(deck=instance, card=card, number=number)
            ci.save()
            instance.cards.add(card)

        return instance

    @property
    def included_cards(self) -> list[tuple[RealCard, int]]:
        """ Список карт, дополненный данными о количестве экземпляров в колоде """

        decklist = list(self.cards.all())
        dbf_ids = [card.dbf_id for card in decklist]
        inclusions = list(Inclusion.objects.filter(card__dbf_id__in=dbf_ids))
        grouped = [(card, inc.number) for card in decklist for inc in inclusions if card.dbf_id == inc.card.dbf_id]

        return sorted(list(set(grouped)), key=lambda card: (card[0].cost, card[0].name))


class Inclusion(models.Model):
    """ Параметры вхождения карты в колоду (Intermediate Model) """
    card = models.ForeignKey(RealCard, on_delete=models.CASCADE)
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE)
    number = models.PositiveSmallIntegerField(verbose_name='Количество',
                                              help_text='Количество вхождений карты в колоду')
