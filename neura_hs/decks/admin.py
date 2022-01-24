from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import Deck, Format
from gallery.models import RealCard, CardSet


class CardInline(admin.StackedInline):
    model = Deck.cards.through
    can_delete = False
    verbose_name = 'Карта'
    verbose_name_plural = 'Карты'
    extra = 0
    raw_id_fields = ('card',)

    def get_queryset(self, request):
        qs = RealCard.includibles.get_queryset()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    def has_change_permission(self, request, obj=None):
        return False


class CardSetInline(admin.StackedInline):
    model = Format.available_sets.through
    can_delete = False
    verbose_name = 'Доступный набор'
    verbose_name_plural = 'Доступные наборы'


@admin.register(Deck)
class DeckAdmin(admin.ModelAdmin):
    inlines = (CardInline,)
    list_display = ('id', 'name', 'author', 'deck_class', 'deck_format', 'created')
    list_filter = ('author', 'deck_class', 'deck_format')
    fieldsets = (
        ('Инфо', {'fields': (('deck_format', 'deck_class'), ('name', 'author'))}),
        (None, {'fields': ('string',)}),
        (None, {'fields': ('created',)})
    )
    readonly_fields = ('created', 'author', 'deck_format', 'deck_class', 'string')
    search_fields = ('name',)
    save_on_top = True

    def get_queryset(self, request):
        """ Переопределение для изменения используемого менеджера Deck """
        qs = self.model.objects.get_queryset()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs


@admin.register(Format)
class FormatAdmin(TranslationAdmin):
    inlines = (CardSetInline,)
