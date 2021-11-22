from django.shortcuts import render
from django.conf import settings
from gallery.models import RealCard, FanCard
from .services.statistics import get_statistics_context


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


def statistics(request):
    context = {'top_menu': settings.TOP_MENU,
               'side_menu': settings.SIDE_MENU,
               'title': 'Статистика'}
    context |= {'statistics': get_statistics_context()}

    return render(request=request, template_name='core/index.html', context=context)
