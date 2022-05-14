from django.urls import path
from . import views

app_name = 'gallery'    # пространство имен urlpatterns

urlpatterns = [
    path('cards/', views.RealCardListView.as_view(), name='realcards'),
    path('card/<slug:card_slug>', views.RealCardDetailView.as_view(), name='real_card'),
]

# (!) Заморожено. Редирект на страницу 'frozen/'
urlpatterns += [
    path('fan_cards/', views.FrozenRedirectView.as_view(), name='fancards'),
    path('fan_card/<slug:card_slug>', views.FrozenRedirectView.as_view(), name='fan_card'),
    path('create_card/', views.FrozenRedirectView.as_view(), name='createcard'),
    path('card_changed/', views.FrozenRedirectView.as_view(), name='card_changed'),
    path('fan_card/<slug:card_slug>/edit/', views.FrozenRedirectView.as_view(), name='updatecard'),
    path('fan_card/<slug:card_slug>/delete/', views.FrozenRedirectView.as_view(), name='deletecard'),
    path('authors/', views.FrozenRedirectView.as_view(), name='authors'),
    path('author/<int:author_id>', views.FrozenRedirectView.as_view(), name='author-detail'),
]
