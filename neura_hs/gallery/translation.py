from modeltranslation.translator import register, TranslationOptions
from .models import RealCard, FanCard, CardClass, Tribe, CardSet, Mechanic


@register(RealCard)
class RealCardTranslationOptions(TranslationOptions):
    fields = ('name', 'text', 'flavor')


@register(CardClass)
class CardClassTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Tribe)
class TribeTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(CardSet)
class CardSetTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Mechanic)
class MechanicTranslationOptions(TranslationOptions):
    fields = ('name',)
