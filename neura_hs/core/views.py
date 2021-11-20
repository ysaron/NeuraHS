from django.shortcuts import render
from django.conf import settings


def about(request):
    context = {'top_menu': settings.TOP_MENU,
               'side_menu': settings.SIDE_MENU,
               'title': 'О сайте'}
    return render(request, 'core/about.html', context=context)


def homepage(request):
    context = {'top_menu': settings.TOP_MENU,
               'side_menu': settings.SIDE_MENU,
               'title': 'NeuraHS'}
    return render(request, 'core/home.html', context=context)


def contact(request):
    context = {'top_menu': settings.TOP_MENU,
               'side_menu': settings.SIDE_MENU,
               'title': 'Связаться'}
    return render(request, 'core/contact.html', context=context)
