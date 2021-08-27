from django.urls import path
from django.views.decorators.cache import cache_page
from . import views

app_name = 'gallery'    # пространство имен urlpatterns

urlpatterns = [
    path('', views.index, name='index'),
    path('fan_cards/', views.FanCardListView.as_view(), name='fancards'),
    path('fan_card/<slug:card_slug>', views.FanCardDetailView.as_view(), name='fan_card'),
    # path('real_cards/', cache_page(60)(views.RealCardListView.as_view()), name='realcards'),
    path('real_cards/', views.RealCardListView.as_view(), name='realcards'),
    path('real_card/<slug:card_slug>', views.RealCardDetailView.as_view(), name='real_card'),
    path('create_card/', views.CreateCard.as_view(), name='createcard'),
    path('card_changed/', views.card_changed, name='card_changed'),
    path('fan_card/<slug:card_slug>/edit/', views.UpdateCard.as_view(), name='updatecard'),
    path('fan_card/<slug:card_slug>/delete/', views.DeleteCard.as_view(), name='deletecard'),
    path('authors/', views.AuthorListView.as_view(), name='authors'),
    path('author/<int:author_id>', views.AuthorDetailView.as_view(), name='author-detail'),
]



