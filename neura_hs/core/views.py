from django.shortcuts import render, redirect
from django.http import HttpRequest, JsonResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from .services.statistics import get_statistics_context


def about(request: HttpRequest):
    context = {'title': _('Site functionality')}
    return render(request, 'core/about.html', context=context)


def homepage(request: HttpRequest):
    context = {'title': 'NeuraHS'}
    return render(request, 'core/home.html', context=context)


def contact(request: HttpRequest):
    if request.GET.get('email') and request.is_ajax():
        response = {'email': 'neurahs@gmail.com'}
        return JsonResponse(response)

    return redirect(reverse_lazy('about'))


def statistics(request: HttpRequest):
    context = {'title': _('Statistics')}
    context |= {'statistics': get_statistics_context()}

    return render(request=request, template_name='core/index.html', context=context)


def api_greeting(request: HttpRequest):
    context = {'title': 'API'}
    return render(request, template_name='core/api.html', context=context)
