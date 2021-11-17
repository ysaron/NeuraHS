from django.urls import path
from . import views


app_name = 'decks'

urlpatterns = [
    path('', views.create_deck, name='index'),
    path('all/', views.NamelessDecksListView.as_view(), name='all_decks'),
    path('my/', views.UserDecksListView.as_view(), name='user_decks'),
    path('<int:deck_id>', views.deck_view, name='deck-detail'),
    path('<int:deck_id>/delete', views.DeckDelete.as_view(), name='deck-delete'),
    path('random_deckstring/', views.get_random_deckstring, name='get_random_deckstring'),
]



