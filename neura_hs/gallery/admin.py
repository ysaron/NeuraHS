from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from modeltranslation.admin import TranslationAdmin
from .models import RealCard, FanCard, CardClass, Tribe, CardSet, Author, Mechanic, HearthstoneState


# (!) Заморожено
class AuthorInline(admin.StackedInline):
    model = Author
    can_delete = False
    verbose_name = 'Автор'
    verbose_name_plural = 'Авторы'


class UserAdmin(BaseUserAdmin):
    inlines = (AuthorInline,)


# Перерегистрация UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# (!) Заморожено
@admin.register(FanCard)
class FanCardAdmin(admin.ModelAdmin):
    """ Класс для доступа к модели Card через админку """
    list_display = ('name', 'author', 'card_type', 'display_card_class', 'creation_date', 'state')
    list_filter = ('author', 'card_type', 'card_class', 'cost', 'attack', 'state')
    fieldsets = (
        ('Общее', {'fields': (('name', 'author'), 'slug')}),
        ('Принадлежность', {'fields': (('card_type', 'card_class'), ('rarity', 'tribe'))}),
        ('Статы', {'fields': ('cost', ('attack', 'health', 'armor', 'durability'))}),
        ('Текст', {'fields': ('text', 'flavor')}),
        ('Доступность', {'fields': ('state',)})
    )
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ('name', 'author__user__username')
    save_on_top = True
    save_as = True
    list_editable = ('state',)


# (!) Заморожено
class FanCardInline(admin.TabularInline):
    """ Для встроенного редактирования связанных записей (только для ForeignKey) """
    pass


@admin.register(RealCard)
class RealCardAdmin(TranslationAdmin):
    list_display = ('name', 'card_type', 'display_card_class', 'card_set', 'creation_date')
    list_filter = ('card_type', 'card_class', 'cost', 'collectible', 'card_set')
    fieldsets = (
        ('Общее', {'fields': (('name_en', 'name_ru', 'slug', 'collectible'),
                              ('card_id', 'dbf_id'),
                              ('image_en', 'image_ru', 'thumbnail'))}),
        ('Принадлежность', {'fields': (('card_type', 'card_class'),
                                       ('rarity', 'tribe'),
                                       'card_set')}),
        ('Статы', {'fields': ('cost',
                              ('attack', 'health', 'armor', 'durability'))}),
        ('Текст', {'fields': ('text', 'flavor')}),
        (None, {'fields': (('artist',),
                           ('mechanic',))}),
    )
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ('card_id', 'dbf_id', 'collectible', 'artist', 'card_type', 'card_set')
    filter_horizontal = ('card_class', 'tribe')
    search_fields = ('name', 'card_set__name', 'text')
    save_on_top = True


@admin.register(CardClass)
class CardClassAdmin(TranslationAdmin):
    pass


@admin.register(Tribe)
class TribeAdmin(TranslationAdmin):
    pass


@admin.register(CardSet)
class CardSetAdmin(TranslationAdmin):
    pass


@admin.register(Mechanic)
class MechanicAdmin(TranslationAdmin):
    pass


@admin.register(HearthstoneState)
class StateAdmin(admin.ModelAdmin):
    pass
