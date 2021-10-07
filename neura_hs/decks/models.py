from django.db import models
from django.utils.translation import gettext_lazy as _
from gallery.models import RealCard, Author, CardClass, CardSet


class Format(models.Model):
    """  """
    class Formats(models.TextChoices):
        UNKNOWN = '', _('---------')
        STANDARD = 'S', _('Standard')
        WILD = 'W', _('Wild')
        CLASSIC = 'C', _('Classic')

    name = models.CharField(max_length=2, choices=Formats.choices, verbose_name='Название')
    available_sets = models.ManyToManyField(CardSet, blank=True, verbose_name='Доступные аддоны',
                                            help_text='Наборы карт, которые можно использовать в данном формате')

    class Meta:
        verbose_name = 'Формат'
        verbose_name_plural = 'Форматы'

    def __str__(self):
        return self.name


class Deck(models.Model):
    """  """
    name = models.CharField(max_length=255, default='', verbose_name='Название',
                            help_text='Название, устанавливаемое пользователем')
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, related_name='decks', null=True, blank=True,
                               verbose_name='Автор', help_text='')
    string = models.CharField(max_length=255, verbose_name='Код колоды',
                              help_text='Код, используемый для определения карт, составляющих колоду')
    cards = models.ManyToManyField(RealCard, verbose_name='Карты', help_text='Карты, составляющие колоду')
    deck_class = models.ForeignKey(CardClass, on_delete=models.CASCADE, related_name='decks', verbose_name='Класс',
                                   help_text='Класс, для которого составлена колода')
    deck_format = models.ForeignKey(Format, default='', on_delete=models.SET_DEFAULT, related_name='decks',
                                    verbose_name='Формат', help_text='Формат, для которого предназначена колода')

    class Meta:
        verbose_name = 'Колода'
        verbose_name_plural = 'Колоды'

    def __str__(self):
        return f'[{self.deck_format}] [{self.deck_class}] {self.name}'
