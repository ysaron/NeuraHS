from django.urls import path
from . import views

app_name = 'api'


urlpatterns = [
    path('cards/', views.RealCardListAPIView.as_view()),
    path('cards/<int:dbf_id>/', views.RealCardDetailAPIView.as_view()),
    path('decks/', views.DeckListAPIView.as_view()),
    path('decks/<int:pk>/', views.DeckDetailAPIView.as_view()),
    path('decode_deck/', views.ViewDeckAPIView.as_view()),
]
