from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.db.models import Model, Manager, QuerySet, Q, Count
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User


class CardQuerySet(QuerySet):

    def search_by_name(self, name):
        return self.filter(name__icontains=name)

    def search_by_rarity(self, rarity):
        return self.filter(rarity=rarity)

    def search_collectible(self, is_collectible: bool):
        return self.filter(collectible=is_collectible)

    def search_by_type(self, type_):
        return self.filter(card_type=type_)

    def search_by_tribe(self, tribe):
        try:
            supertribe = Tribe.objects.get(service_name='All')
            return self.filter(Q(tribe=tribe) | Q(tribe=supertribe))
        except Tribe.DoesNotExist:
            return self.filter(tribe=tribe)

    def search_by_class(self, class_):
        return self.filter(card_class=class_)

    def search_by_set(self, set_):
        return self.filter(card_set=set_)

    def search_by_mechanic(self, mechanic: str):
        """ Поиск записей с установленным в True полем mechanic """
        return self.filter(**{mechanic: True}) if Card.field_exists(mechanic) else self.all()

    def confirmed(self):
        return self.filter(state=True)


class IncludibleCardManager(Manager):
    """ Доступ к картам, которые можно включить в колоду """

    def get_queryset(self):
        return super().get_queryset().filter(Q(collectible=True) & ~Q(card_set__service_name='Hero Skins'))


class AuthorManager(Manager):

    def active(self):
        """ Возвращает QuerySet с авторами, имеющими хотя бы 1 прошедшую премодерацию карту """
        authors = self.get_queryset().annotate(num_fancards=Count('fancard', filter=Q(fancard__state=True)))
        return authors.exclude(num_fancards=0)


class Author(Model):
    """ Модель автора фан-карт, расширяющая модель User """
    user: User = models.OneToOneField(User, on_delete=models.CASCADE)
    about = models.TextField(blank=True, default='')

    objects = AuthorManager()

    class Meta:
        ordering = ['user']

    def __str__(self):
        """ Строковое представление автора """
        return self.user.username

    def get_absolute_url(self):
        """ Возвращает URL для доступа к странице автора """
        return reverse('gallery:author-detail', kwargs={'author_id': self.id})


@receiver(post_save, sender=User)
def update_profile_signal(sender, instance, created, **kwargs):
    """ При регистрации пользователя создает соответствующий объект Автора """
    if created:
        Author.objects.create(user=instance)
    instance.author.save()


class CardClass(Model):
    """ Модель игрового класса (Маг, Паладин и т.д.) """

    name = models.CharField(max_length=255, help_text=_('The name of the in-game class.'),
                            verbose_name=_('Class'))
    service_name = models.CharField(max_length=255, verbose_name='Service', default='', help_text='(!)',
                                    unique=True)
    collectible = models.BooleanField(default=False, verbose_name=_('Collectible'))

    class Meta:
        verbose_name = _('In-game class')
        verbose_name_plural = _('In-game classes')

    def __str__(self):
        """ Строковое представление объекта модели """
        return self.name if self.collectible else f'[{self.name}]'


class Tribe(Model):
    """ Модель расы (мурлок, демон и т.д.) """

    name = models.CharField(max_length=255, verbose_name=_('The tribe of the minion.'))
    service_name = models.CharField(max_length=255, verbose_name='Service', default='', help_text='(!)',
                                    unique=True)

    class Meta:
        verbose_name = _('The tribe of the minion.')
        verbose_name_plural = _('The tribes of the minion.')

    def __str__(self):
        """ Строковое представление объекта модели """
        return self.name


class CardSet(Model):
    """ Модель набора карт Hearthstone """
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    service_name = models.CharField(max_length=255, verbose_name='Service', default='', help_text='(!)', blank=True)

    class Meta:
        verbose_name = _('Set')
        verbose_name_plural = _('Sets')

    def __str__(self):
        """ Строковое представление объекта модели """
        return self.name


class Card(Model):
    """ Абстрактная модель карты Hearthstone """

    class CardTypes(models.TextChoices):
        UNKNOWN = '', _('---------')
        MINION = 'M', _('Minion')
        SPELL = 'S', _('Spell')
        HERO = 'H', _('Hero')
        WEAPON = 'W', _('Weapon')
        HEROPOWER = 'HP', _('Hero power')

    class Rarities(models.TextChoices):
        UNKNOWN = '', _('---------')
        NO_RARITY = 'NO', _('No rarity')
        COMMON = 'C', _('Common')
        RARE = 'R', _('Rare')
        EPIC = 'E', _('Epic')
        LEGENDARY = 'L', _('Legendary')

    class SpellSchools(models.TextChoices):
        UNKNOWN = '', _('---------')
        HOLY = 'H', _('Holy')
        SHADOW = 'SH', _('Shadow')
        NATURE = 'N', _('Nature')
        FEL = 'F', _('Fel')
        FIRE = 'FI', _('Fire')
        FROST = 'FR', _('Frost')
        ARCANE = 'A', _('Arcane')

    class Mechanics(models.TextChoices):
        UNKNOWN = '', _('---------')
        SILENCE = 'silence', _('Silence')
        BATTLECRY = 'battlecry', _('Battlecry')
        DIVINE_SHIELD = 'divine_shield', _('Divine shield')
        STEALTH = 'stealth', _('Stealth')
        OVERLOAD = 'overload', _('Overload')
        WINDFURY = 'windfury', _('Windfury')
        SECRET = 'secret', _('Secret')
        CHARGE = 'charge', _('Charge')
        DEATHRATTLE = 'deathrattle', _('Deathrattle')
        TAUNT = 'taunt', _('Taunt')
        SPELL_DAMAGE = 'spell_damage', _('Spell damage')
        COMBO = 'combo', _('Combo')
        AURA = 'aura', _('Aura')
        POISON = 'poison', _('Poison')
        FREEZE = 'freeze', _('Freeze')
        RUSH = 'rush', _('Rush')
        SPELL_IMMUNE = 'spell_immune', _('Spell immune')
        LIFESTEAL = 'lifesteal', _('Lifesteal')
        CASTS_WHEN_DRAWN = 'casts_when_drawn', _('Casts when drawn')
        INSPIRE = 'inspire', _('Inspire')
        SPELL_BURST = 'spell_burst', _('Spellburst')
        DISCOVER = 'discover', _('Discover')
        ECHO = 'echo', _('Echo')
        QUEST = 'quest', _('Quest')
        SIDE_QUEST = 'side_quest', _('Side quest')
        ONE_TURN_EFFECT = 'one_turn_effect', _('One turn effect')
        REBORN = 'reborn', _('Reborn')
        OUTCAST = 'outcast', _('Outcast')
        MAGNETIC = 'magnetic', _('Magnetic')
        RECRUIT = 'recruit', _('Recruit')
        CORRUPT = 'corrupt', _('Corrupt')
        TWINSPELL = 'twinspell', _('Twinspell')
        JADE_GOLEM = 'jade_golem', _('Jade golem')
        ADAPT = 'adapt', _('Adapt')
        OVERKILL = 'overkill', _('Overkill')
        INVOKE = 'invoke', _('Invoke')
        BLOOD_GEM = 'blood_gem', _('Blood gem')
        FRENZY = 'frenzy', _('Frenzy')
        TRADEABLE = 'tradeable', _('Tradeable')
        QUESTLINE = 'questline', _('Questline')

    name = models.CharField(max_length=255, verbose_name=_('Name'))
    service_name = models.CharField(max_length=255, default='')
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name='URL')
    author = models.CharField(max_length=255, default='', verbose_name=_('Author'))
    card_type = models.CharField(max_length=2, choices=CardTypes.choices, default=CardTypes.UNKNOWN,
                                 verbose_name=_('Type'))
    card_class = models.ManyToManyField(CardClass, verbose_name=_('Class'),
                                        help_text=_('You can select from 1 to 3 classes [Ctrl + LMB].'))
    cost = models.SmallIntegerField(blank=True, null=True, default=0, verbose_name=_('Cost (mana)'),
                                    validators=[MinValueValidator(0)])
    attack = models.SmallIntegerField(blank=True, null=True, default=0, verbose_name=_('Attack'),
                                      help_text=_('For minions and weapons only.'),
                                      validators=[MinValueValidator(0)])
    health = models.SmallIntegerField(blank=True, null=True, default=0, verbose_name=_('Health'),
                                      help_text=_('For minions only.'),
                                      validators=[MinValueValidator(0)])
    durability = models.SmallIntegerField(blank=True, null=True, default=0, verbose_name=_('Durability'),
                                          help_text=_('For weapons only.'),
                                          validators=[MinValueValidator(0)])
    armor = models.SmallIntegerField(blank=True, null=True, default=0, verbose_name=_('Armor'),
                                     help_text=_('For hero cards only.'),
                                     validators=[MinValueValidator(0)])
    text = models.TextField(max_length=1000, blank=True, default='', verbose_name=_('Text'),
                            help_text=_('The text of the card that defines its properties.'))
    flavor = models.TextField(max_length=1000, blank=True, default='', verbose_name=_('Flavor'),
                              help_text=_('Free text.'))
    rarity = models.CharField(max_length=2, choices=Rarities.choices, verbose_name=_('Rarity'),
                              default=Rarities.UNKNOWN)
    tribe = models.ManyToManyField(Tribe, blank=True, verbose_name=_('Tribe'),
                                   help_text=_('For creatures only. You can select from 0 to 2 races [Ctrl + LMB].'))
    spell_school = models.CharField(max_length=2, choices=SpellSchools.choices, default=SpellSchools.UNKNOWN,
                                    verbose_name=_('Spell school'), blank=True, help_text=_('For spells only.'))
    creation_date = models.DateTimeField(null=True, blank=True, auto_now_add=True,
                                         verbose_name=_('Date of creation'))
    battlegrounds = models.BooleanField(default=False, verbose_name=_('Battlegrounds card'))

    # поля, отражающие механики Hearthstone, используемые картой
    silence = models.BooleanField(default=False, verbose_name=Mechanics.SILENCE.label)
    battlecry = models.BooleanField(default=False, verbose_name=Mechanics.SILENCE.label)
    divine_shield = models.BooleanField(default=False, verbose_name=Mechanics.SILENCE.label)
    stealth = models.BooleanField(default=False, verbose_name=Mechanics.SILENCE.label)
    overload = models.BooleanField(default=False, verbose_name=Mechanics.SILENCE.label)
    windfury = models.BooleanField(default=False, verbose_name=Mechanics.SILENCE.label)
    secret = models.BooleanField(default=False, verbose_name=Mechanics.SILENCE.label)
    charge = models.BooleanField(default=False, verbose_name=Mechanics.SILENCE.label)
    deathrattle = models.BooleanField(default=False, verbose_name=Mechanics.SILENCE.label)
    taunt = models.BooleanField(default=False, verbose_name=Mechanics.SILENCE.label)
    spell_damage = models.BooleanField(default=False, verbose_name=Mechanics.SILENCE.label)
    combo = models.BooleanField(default=False, verbose_name=Mechanics.SILENCE.label)
    aura = models.BooleanField(default=False, verbose_name=Mechanics.SILENCE.label)
    poison = models.BooleanField(default=False, verbose_name=Mechanics.SILENCE.label)
    freeze = models.BooleanField(default=False, verbose_name=Mechanics.SILENCE.label)
    rush = models.BooleanField(default=False, verbose_name=Mechanics.SILENCE.label)
    spell_immune = models.BooleanField(default=False, verbose_name=Mechanics.SILENCE.label)
    lifesteal = models.BooleanField(default=False, verbose_name=Mechanics.SILENCE.label)
    casts_when_drawn = models.BooleanField(default=False, verbose_name=Mechanics.SILENCE.label)
    inspire = models.BooleanField(default=False, verbose_name=Mechanics.SILENCE.label)
    spell_burst = models.BooleanField(default=False, verbose_name=Mechanics.SILENCE.label)
    discover = models.BooleanField(default=False, verbose_name=Mechanics.SILENCE.label)
    echo = models.BooleanField(default=False, verbose_name=Mechanics.SILENCE.label)
    quest = models.BooleanField(default=False, verbose_name=Mechanics.SILENCE.label)
    side_quest = models.BooleanField(default=False, verbose_name=Mechanics.SILENCE.label)
    one_turn_effect = models.BooleanField(default=False, verbose_name=Mechanics.SILENCE.label)
    reborn = models.BooleanField(default=False, verbose_name=Mechanics.SILENCE.label)
    outcast = models.BooleanField(default=False, verbose_name=Mechanics.SILENCE.label)
    magnetic = models.BooleanField(default=False, verbose_name=Mechanics.SILENCE.label)
    recruit = models.BooleanField(default=False, verbose_name=Mechanics.SILENCE.label)
    corrupt = models.BooleanField(default=False, verbose_name=Mechanics.SILENCE.label)
    twinspell = models.BooleanField(default=False, verbose_name=Mechanics.SILENCE.label)
    jade_golem = models.BooleanField(default=False, verbose_name=Mechanics.SILENCE.label)
    adapt = models.BooleanField(default=False, verbose_name=Mechanics.SILENCE.label)
    overkill = models.BooleanField(default=False, verbose_name=Mechanics.SILENCE.label)
    invoke = models.BooleanField(default=False, verbose_name=Mechanics.SILENCE.label)
    blood_gem = models.BooleanField(default=False, verbose_name=Mechanics.SILENCE.label)
    frenzy = models.BooleanField(default=False, verbose_name=Mechanics.SILENCE.label)
    tradeable = models.BooleanField(default=False, verbose_name=Mechanics.SILENCE.label)
    questline = models.BooleanField(default=False, verbose_name=Mechanics.SILENCE.label)

    class Meta:
        abstract = True     # данный класс - не модель. Модели от него наследуются

    # Для отображения в админ-панели
    def display_card_class(self):
        """
        Создает строку для поля card_class. Необходимо для отображения поля типа ManyToMany в списке в админ-панели
        """
        return ', '.join([cardclass.name for cardclass in self.card_class.all()])

    display_card_class.short_description = _('Class')

    @classmethod
    def field_exists(cls, field):
        """ Проверка на существование поля field в модели """
        try:
            cls._meta.get_field(field)
            return True
        except FieldDoesNotExist:
            return False

    @property
    def mechanics_list(self):
        """ Список механик Hearthstone, связанных с картой """
        return [str(value) for key, value in Card.Mechanics.choices if Card.field_exists(key) and getattr(self, key)]


class RealCard(Card):
    """ Модель существующей карты. Экземпляры создаются скриптом """

    card_id = models.CharField(max_length=255, default='', help_text=_('String ID of an existing card'))
    dbf_id = models.IntegerField(null=True, unique=True, help_text=_('Integer ID of an existing card'))
    card_set = models.ForeignKey(CardSet, on_delete=models.SET_NULL, null=True, verbose_name=_('Set'),
                                 related_name='cardsets')
    artist = models.CharField(max_length=255, blank=True, verbose_name=_('Artist'))
    collectible = models.BooleanField(default=True, verbose_name=_('Collectible'))

    objects = CardQuerySet.as_manager()
    includibles = IncludibleCardManager()

    class Meta(Card.Meta):
        verbose_name = _('Hearthstone card')
        verbose_name_plural = _('Hearthstone cards')
        ordering = ['-cost']

    def __str__(self):
        """ Строковое представление объекта модели """
        return self.name if self.collectible else f'[{self.name}]'

    def get_absolute_url(self):
        """ Возвращает URL для доступа к подробной странице карты """
        return reverse('gallery:real_card', kwargs={'card_slug': self.slug})


class FanCard(Card):
    """ Модель фановой карты. Экземпляры создаются юзерами через формы """

    author = models.ForeignKey(Author, on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_('Author'))
    state = models.BooleanField(default=False, verbose_name=_('Display'))

    objects = CardQuerySet.as_manager()

    class Meta(Card.Meta):
        verbose_name = _('Fan card')
        verbose_name_plural = _('Fan cards')
        ordering = ['-creation_date', 'name']

    def __str__(self):
        """ Строковое представление объекта модели """
        return self.name

    def get_absolute_url(self):
        """ Возвращает URL для доступа к подробной странице карты """
        return reverse('gallery:fan_card', kwargs={'card_slug': self.slug})
