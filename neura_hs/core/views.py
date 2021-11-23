from django.shortcuts import render, redirect
from django.http import HttpRequest, JsonResponse
from django.conf import settings
from django.urls import reverse_lazy

from gallery.models import RealCard, FanCard
from .services.statistics import get_statistics_context


def about(request: HttpRequest):
    context = {'top_menu': settings.TOP_MENU,
               'side_menu': settings.SIDE_MENU,
               'title': 'Функционал сайта'}
    return render(request, 'core/about.html', context=context)


def homepage(request: HttpRequest):
    context = {'top_menu': settings.TOP_MENU,
               'side_menu': settings.SIDE_MENU,
               'title': 'NeuraHS'}
    return render(request, 'core/home.html', context=context)


def contact(request: HttpRequest):
    if request.GET.get('email') and request.is_ajax():
        response = {'email': 'neurahs@gmail.com'}
        return JsonResponse(response)

    return redirect(reverse_lazy('about'))


def statistics(request: HttpRequest):
    context = {'top_menu': settings.TOP_MENU,
               'side_menu': settings.SIDE_MENU,
               'title': 'Статистика'}
    context |= {'statistics': get_statistics_context()}

    return render(request=request, template_name='core/index.html', context=context)
