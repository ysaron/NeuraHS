from django.urls import path
from . import views

app_name = 'api'


urlpatterns = [
    path('cards/', views.RealCardViewSet.as_view({'get': 'list'})),
    path('cards/<int:dbf_id>/', views.RealCardViewSet.as_view({'get': 'retrieve'})),
    path('decks/', views.DeckListAPIView.as_view()),
    path('decks/<int:pk>/', views.DeckDetailAPIView.as_view()),
    path('decode_deck/', views.ViewDeckAPIView.as_view()),
]
