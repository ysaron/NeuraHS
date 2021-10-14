from django.urls import path
from . import views


app_name = 'decks'

urlpatterns = [
    path('', views.main, name='index'),
]



