from django.shortcuts import render
from django.conf import settings
from utils.handlers import log_all_exceptions


@log_all_exceptions
def about(request):
    context = {'top_menu': settings.TOP_MENU,
               'side_menu': settings.SIDE_MENU,
               'title': 'О сайте'}
    return render(request, 'core/about.html', context=context)


@log_all_exceptions
def homepage(request):
    context = {'top_menu': settings.TOP_MENU,
               'side_menu': settings.SIDE_MENU,
               'title': 'NeuraHS'}
    return render(request, 'core/home.html', context=context)


@log_all_exceptions
def contact(request):
    context = {'top_menu': settings.TOP_MENU,
               'side_menu': settings.SIDE_MENU,
               'title': 'Связаться'}
    return render(request, 'core/contact.html', context=context)
