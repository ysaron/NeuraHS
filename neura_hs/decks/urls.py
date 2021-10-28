from django.urls import path
from . import views


app_name = 'decks'

urlpatterns = [
    path('', views.main, name='index'),
    path('all/', views.DeckListView.as_view(), name='decks'),
    path('all/<int:deck_id>', views.NamelessDeckDetailView.as_view(), name='deck-detail'),
]



